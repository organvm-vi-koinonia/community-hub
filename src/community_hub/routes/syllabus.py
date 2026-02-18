"""Syllabus routes — generate and view personalized learning paths."""

from __future__ import annotations

from uuid import uuid4

from fastapi import APIRouter, HTTPException, Request
from sqlalchemy import select

from koinonia_db.models.salon import TaxonomyNodeRow
from koinonia_db.models.reading import Entry
from koinonia_db.models.syllabus import LearnerProfileRow, LearningPathRow, LearningModuleRow

router = APIRouter()

ORGAN_MAP = {
    "I": "i-theoria",
    "II": "ii-poiesis",
    "III": "iii-ergon",
    "IV": "iv-taxis",
    "V": "v-logos",
    "VI": "vi-koinonia",
    "VII": "vii-kerygma",
    "VIII": "viii-meta",
}

DIFFICULTY_ORDER = {"beginner": 0, "intermediate": 1, "advanced": 2}


async def _generate_path(db_session, organs: list[str], level: str, name: str) -> dict:
    """Generate a learning path from DB data and persist it."""
    # Load taxonomy
    roots = (await db_session.execute(
        select(TaxonomyNodeRow).where(TaxonomyNodeRow.parent_id.is_(None))
    )).scalars().all()

    taxonomy = {}
    for root in roots:
        children = (await db_session.execute(
            select(TaxonomyNodeRow).where(TaxonomyNodeRow.parent_id == root.id)
        )).scalars().all()
        taxonomy[root.slug] = {
            "label": root.label,
            "children": [{"slug": c.slug, "label": c.label} for c in children],
        }

    # Load readings
    entries = (await db_session.execute(select(Entry))).scalars().all()
    readings = [
        {"title": e.title, "organ_tags": e.organ_tags or [], "difficulty": e.difficulty}
        for e in entries
    ]

    # Build modules
    if level == "beginner":
        allowed = {"beginner", "intermediate"}
    elif level == "intermediate":
        allowed = {"intermediate", "advanced"}
    else:
        allowed = {"advanced"}

    modules = []
    for organ_code in organs:
        organ_slug = ORGAN_MAP.get(organ_code, organ_code.lower())
        organ_node = taxonomy.get(organ_slug)
        if not organ_node:
            continue

        organ_readings = [
            r for r in readings
            if any(
                tag.startswith(organ_slug.split("-")[0] + "-") or tag == organ_slug
                for tag in r.get("organ_tags", [])
            )
        ]
        filtered = [r for r in organ_readings if r.get("difficulty", "intermediate") in allowed]

        for child in organ_node.get("children", []):
            child_readings = [r["title"] for r in filtered][:3]
            if not child_readings:
                child_readings = [f"See {organ_node['label']} documentation"]

            modules.append({
                "module_id": f"{child['slug']}-{level[:3]}",
                "title": child["label"],
                "organ": organ_slug,
                "difficulty": level,
                "readings": child_readings,
                "questions": [
                    f"What is the core idea behind {child['label']}?",
                    f"How does {child['label']} connect to {organ_node['label']}?",
                    f"What would you build or explore using {child['label']}?",
                ],
                "estimated_hours": 2.0 if level != "advanced" else 3.0,
            })

    modules.sort(key=lambda m: DIFFICULTY_ORDER.get(m["difficulty"], 1))
    total_hours = sum(m["estimated_hours"] for m in modules)

    # Persist
    path_id = uuid4().hex[:8]
    learner = LearnerProfileRow(
        name=name or "anonymous",
        organs_of_interest=organs,
        level=level,
    )
    db_session.add(learner)
    await db_session.flush()

    path_row = LearningPathRow(
        path_id=path_id,
        title=f"Learning Path: {', '.join(organs)}",
        learner_id=learner.id,
        total_hours=total_hours,
    )
    db_session.add(path_row)
    await db_session.flush()

    for i, mod in enumerate(modules):
        db_session.add(LearningModuleRow(
            path_id=path_row.id,
            module_id=mod["module_id"],
            title=mod["title"],
            organ=mod["organ"],
            difficulty=mod["difficulty"],
            readings=mod["readings"],
            questions=mod["questions"],
            estimated_hours=mod["estimated_hours"],
            seq=i,
        ))

    await db_session.commit()

    return {
        "path_id": path_id,
        "title": path_row.title,
        "organs": organs,
        "level": level,
        "total_hours": total_hours,
        "modules": modules,
    }


@router.get("/syllabus")
async def syllabus_form(request: Request):
    """Show the syllabus generation form."""
    templates = request.app.state.templates
    return templates.TemplateResponse("syllabus/form.html", {"request": request})


@router.post("/syllabus/generate")
async def syllabus_generate(request: Request):
    """Generate a learning path from form submission."""
    templates = request.app.state.templates
    form = await request.form()
    organs = form.getlist("organs")
    level = form.get("level", "beginner")
    name = form.get("name", "anonymous")

    if not organs:
        return templates.TemplateResponse("syllabus/form.html", {
            "request": request,
            "error": "Select at least one organ.",
        })

    async with request.app.state.db() as session:
        path = await _generate_path(session, organs, level, name)

    return templates.TemplateResponse("syllabus/path.html", {
        "request": request,
        "path": path,
    })


@router.get("/syllabus/{path_id}")
async def syllabus_view(request: Request, path_id: str):
    """View a previously generated learning path."""
    templates = request.app.state.templates
    async with request.app.state.db() as session:
        stmt = select(LearningPathRow).where(LearningPathRow.path_id == path_id)
        path_row = (await session.execute(stmt)).scalar_one_or_none()
        if not path_row:
            raise HTTPException(status_code=404, detail="Learning path not found")

        learner = await session.get(LearnerProfileRow, path_row.learner_id)
        modules_stmt = select(LearningModuleRow).where(
            LearningModuleRow.path_id == path_row.id
        ).order_by(LearningModuleRow.seq)
        modules = (await session.execute(modules_stmt)).scalars().all()

    path = {
        "path_id": path_row.path_id,
        "title": path_row.title,
        "organs": learner.organs_of_interest if learner else [],
        "level": learner.level if learner else "beginner",
        "total_hours": path_row.total_hours,
        "modules": [
            {
                "module_id": m.module_id,
                "title": m.title,
                "organ": m.organ,
                "difficulty": m.difficulty,
                "readings": m.readings or [],
                "questions": m.questions or [],
                "estimated_hours": m.estimated_hours,
            }
            for m in modules
        ],
    }

    return templates.TemplateResponse("syllabus/path.html", {
        "request": request,
        "path": path,
    })


@router.get("/api/syllabus/generate")
async def api_syllabus_generate(
    request: Request,
    organs: str = "I",
    level: str = "beginner",
    name: str = "api-user",
):
    """JSON API — generate a learning path. Organs as comma-separated string."""
    organ_list = [o.strip() for o in organs.split(",") if o.strip()]
    if not organ_list:
        return {"error": "Provide at least one organ code (e.g., organs=I,II)"}

    valid_levels = {"beginner", "intermediate", "advanced"}
    if level not in valid_levels:
        return {"error": f"Level must be one of {valid_levels}"}

    async with request.app.state.db() as session:
        path = await _generate_path(session, organ_list, level, name)

    return path
