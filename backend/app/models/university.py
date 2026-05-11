"""
University Model - Data access layer for universities (SQLAlchemy ORM session).

All queries use SQLAlchemy ORM — no raw SQL.
"""
from sqlalchemy.orm import Session, joinedload, subqueryload
from sqlalchemy import cast, func, Numeric
from app.entities.university import University
from app.entities.country import Country
from app.entities.detail_infor import DetailInfor
from app.entities.entry_infor import EntryInfor
from app.entities.score import Score
from app.entities.indicator import Indicator
from app.entities.score_type import ScoreType
from app.entities.enums import REGION_LABELS
from typing import Optional, Dict, Any, List


def _eager_opts():
    """Standard joinedload options to fetch scores + country in one query."""
    return [
        joinedload(University.country),
        subqueryload(University.score_list)
        .joinedload(Score.indicator)
        .joinedload(Indicator.score_type),
    ]


def _uni_to_dict(uni: University) -> Dict[str, Any]:
    """Convert an ORM University (with eager-loaded relationships) to the response dict."""
    scores: Dict[str, Dict[str, Optional[float]]] = {}
    for sc in uni.score_list:
        if sc.indicator and sc.indicator.score_type:
            cat = sc.indicator.score_type.name
            ind = sc.indicator.name
            scores.setdefault(cat, {})[ind] = sc.score

    region_id = uni.country.region_id if uni.country else None
    return {
        "id": uni.id,
        "name": uni.name,
        "region_id": region_id,
        "region": REGION_LABELS.get(region_id) if region_id else None,
        "country_id": uni.country_id,
        "city": uni.city,
        "logo": uni.logo,
        "overall_score": uni.overall_score,
        "rank": uni.rank_int,
        "rank_int": uni.rank_int,
        "path": uni.path,
        "country": uni.country.name if uni.country else None,
        "country_name": uni.country.name if uni.country else None,
        "scores": scores,
    }


class UniversityModel:

    @staticmethod
    def get_all_universities(
        db: Session,
        limit: int = 20,
        page: int = 1,
    ) -> Dict[str, Any]:
        offset = (page - 1) * limit
        base_query = (
            db.query(University)
            .order_by(University.rank_int.asc(), University.id.asc())
        )
        total = base_query.count()
        unis = (
            base_query
            .options(*_eager_opts())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return {
            "data": [_uni_to_dict(u) for u in unis],
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": (total + limit - 1) // limit,
        }

    @staticmethod
    def search_universities_by_name(
        db: Session,
        name: str,
        limit: int = 20,
        page: int = 1,
    ) -> Dict[str, Any]:
        offset = (page - 1) * limit
        base_query = (
            db.query(University)
            .filter(University.name.ilike(f"%{name}%"))
            .order_by(University.rank_int.asc())
        )
        total = base_query.count()
        unis = (
            base_query
            .options(*_eager_opts())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return {
            "data": [_uni_to_dict(u) for u in unis],
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": (total + limit - 1) // limit,
        }

    @staticmethod
    def get_regions(db: Session) -> List[dict]:
        from app.entities.country import Country
        used_ids = (
            db.query(Country.region_id)
            .filter(Country.region_id.isnot(None))
            .distinct()
            .all()
        )
        ids = sorted({row[0] for row in used_ids})
        return [{"id": rid, "name": REGION_LABELS[rid]} for rid in ids if rid in REGION_LABELS]

    @staticmethod
    def get_countries_by_region(db: Session, region_id: Optional[int] = None) -> List[Dict[str, Any]]:
        from app.entities.country import Country
        query = db.query(Country)
        if region_id is not None:
            query = query.filter(Country.region_id == region_id)
        results = query.order_by(Country.name).all()
        return [{"id": r.id, "name": r.name} for r in results]

    TEST_COLUMN_MAP = {
        "IELTS": "IELTS",
        "TOEFL": "TOEFL",
        "SAT":   "SAT",
        "GRE":   "GRE",
        "GMAT":  "GMAT",
        "ACT":   "ACT",
        "ATAR":  "ATAR",
        "GPA":   "GPA",
    }

    @staticmethod
    def filter_universities(
        db: Session,
        region_id: Optional[int] = None,
        country: Optional[str] = None,
        city: Optional[str] = None,
        min_rank: Optional[int] = None,
        max_rank: Optional[int] = None,
        english_tests: Optional[List[str]] = None,
        academic_tests: Optional[List[str]] = None,
        min_international_pct: Optional[float] = None,
        fee_min: Optional[float] = None,
        fee_max: Optional[float] = None,
        scholarship: Optional[str] = None,
        limit: int = 20,
        page: int = 1,
    ) -> Dict[str, Any]:
        query = db.query(University).options(*_eager_opts())

        # Country/region filters require a join to countries
        if region_id is not None or country:
            query = query.join(Country, University.country_id == Country.id)
            if region_id is not None:
                query = query.filter(Country.region_id == region_id)
            if country:
                query = query.filter(Country.name == country)

        if city:
            query = query.filter(University.city.ilike(f"%{city}%"))
        if min_rank is not None:
            query = query.filter(University.rank_int >= min_rank)
        if max_rank is not None:
            query = query.filter(University.rank_int <= max_rank)

        # Entry test filters: university must have at least one entry_infor row
        # with the given test column non-null
        TEST_ATTR_MAP = {
            "IELTS": EntryInfor.ielts,
            "TOEFL": EntryInfor.toefl,
            "SAT":   EntryInfor.sat,
            "GRE":   EntryInfor.gre,
            "GMAT":  EntryInfor.gmat,
            "ACT":   EntryInfor.act,
            "ATAR":  EntryInfor.atar,
            "GPA":   EntryInfor.gpa,
        }
        all_tests = list(english_tests or []) + list(academic_tests or [])
        for test_name in all_tests:
            col = TEST_ATTR_MAP.get(test_name)
            if col is not None:
                query = query.filter(
                    University.entry_infors.any(col.isnot(None))
                )

        # Detail info filters
        if min_international_pct is not None and min_international_pct > 0:
            # Cast the stored string (e.g. "45%") to a number for comparison
            query = query.filter(
                University.detail_infor.has(
                    cast(
                        func.replace(func.replace(DetailInfor.international, "%", ""), " ", ""),
                        Numeric(5, 2),
                    ) >= min_international_pct
                )
            )

        if fee_min is not None:
            query = query.filter(
                University.detail_infor.has(DetailInfor.fee >= str(fee_min))
            )
        if fee_max is not None:
            query = query.filter(
                University.detail_infor.has(DetailInfor.fee <= str(fee_max))
            )

        if scholarship == "yes":
            query = query.filter(
                University.detail_infor.has(DetailInfor.scholarship == True)
            )
        elif scholarship == "no":
            query = query.filter(
                University.detail_infor.has(DetailInfor.scholarship == False)
            )

        offset = (page - 1) * limit
        total = query.count()
        unis = (
            query
            .order_by(University.rank_int.asc(), University.id.asc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return {
            "data": [_uni_to_dict(u) for u in unis],
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": (total + limit - 1) // limit,
        }


    @staticmethod
    def get_university_by_id(db: Session, university_id: int) -> Optional[Dict[str, Any]]:
        uni = (
            db.query(University)
            .options(*_eager_opts())
            .filter(University.id == university_id)
            .first()
        )
        return _uni_to_dict(uni) if uni else None

    @staticmethod
    def get_scholarships(db: Session, university_id: int) -> List[Dict[str, Any]]:
        from app.entities.scholarship import Scholarship
        rows = db.query(Scholarship).filter(Scholarship.university_id == university_id).all()
        return [r.to_dict() for r in rows]

    @staticmethod
    def _parse_score(value) -> Optional[float]:
        if value is None:
            return None
        try:
            cleaned = str(value).replace("+", "").strip()
            return float(cleaned) if cleaned else None
        except (ValueError, TypeError):
            return None

    @staticmethod
    def get_entry_requirements(db: Session, university_id: int, degree_type: int = None) -> Optional[Dict[str, Any]]:
        uni = db.query(University).filter(University.id == university_id).first()
        if not uni:
            return None

        entry_rows = (
            db.query(EntryInfor)
            .filter(EntryInfor.university_id == university_id)
            .all()
        )

        out: Dict[str, Any] = {
            "name": uni.name,
            "rank": uni.rank_int,
            "bachelor": None,
            "master": None,
        }

        for ei in entry_rows:
            req_data = {
                "sat":   UniversityModel._parse_score(ei.sat),
                "gre":   UniversityModel._parse_score(ei.gre),
                "gmat":  UniversityModel._parse_score(ei.gmat),
                "act":   UniversityModel._parse_score(ei.act),
                "atar":  UniversityModel._parse_score(ei.atar),
                "gpa":   UniversityModel._parse_score(ei.gpa),
                "toefl": UniversityModel._parse_score(ei.toefl),
                "ielts": UniversityModel._parse_score(ei.ielts),
            }
            if ei.degree_type == EntryInfor.DEGREE_BACHELOR:
                out["bachelor"] = req_data
            elif ei.degree_type == EntryInfor.DEGREE_MASTER:
                out["master"] = req_data

        return out

    @staticmethod
    def get_detail_information(db: Session, university_id: int) -> Optional[Dict[str, Any]]:
        uni = db.query(University).filter(University.id == university_id).first()
        if not uni:
            return None
        di = (
            db.query(DetailInfor)
            .filter(DetailInfor.university_id == university_id)
            .first()
        )
        if not di:
            # Return empty detail for this university
            di = DetailInfor(university_id=university_id)
        return di.to_dict()

    @staticmethod
    def get_comparison_data(db: Session, university_ids: List[int]) -> List[Dict[str, Any]]:
        if not university_ids:
            return []
        unis = (
            db.query(University)
            .options(joinedload(University.detail_infor))
            .filter(University.id.in_(university_ids))
            .all()
        )
        result = []
        for uni in unis:
            di = uni.detail_infor or DetailInfor(university_id=uni.id)
            row = di.to_dict()
            row["id"] = uni.id
            row["name"] = uni.name
            result.append(row)
        return result

    @staticmethod
    def get_chart_data(db: Session, university_ids: List[int]) -> List[Dict[str, Any]]:
        if not university_ids:
            return []
        unis = (
            db.query(University)
            .options(joinedload(University.entry_infors))
            .filter(University.id.in_(university_ids))
            .all()
        )

        def _ei_scores(ei: EntryInfor) -> Dict[str, Optional[float]]:
            return {k: UniversityModel._parse_score(getattr(ei, k)) for k in
                    ("sat", "gre", "gmat", "act", "atar", "gpa", "toefl", "ielts")}

        uni_map: Dict[int, Dict] = {}
        for uni in unis:
            entry = {"id": uni.id, "name": uni.name, "bachelor": None, "master": None}
            for ei in uni.entry_infors:
                if ei.degree_type == EntryInfor.DEGREE_BACHELOR:
                    entry["bachelor"] = _ei_scores(ei)
                elif ei.degree_type == EntryInfor.DEGREE_MASTER:
                    entry["master"] = _ei_scores(ei)
            uni_map[uni.id] = entry

        return [uni_map[uid] for uid in university_ids if uid in uni_map]

    # ── indicator key → indicator_id (from DB) ───────────────────────────────
    _INDICATOR_MAP = {
        "academic_reputation":      76,
        "citations_per_faculty":    73,
        "intl_research_network":    15,
        "faculty_student_ratio":    36,
        "employer_reputation":      77,
        "employment_outcomes":      3819456,
        "intl_student_ratio":       14,
        "intl_faculty_ratio":       18,
        "intl_student_diversity":   3924415,
        "sustainability_score":     3897497,
    }

    @staticmethod
    def create_university(db: Session, data: dict) -> dict:
        """Insert university + detail_infor + entry_infor + scores rows."""
        # 1. universities
        uni = University(
            name=data.get("name", ""),
            city=data.get("city"),
            country_id=data.get("country_id") or None,
            logo=data.get("logo"),
            path=data.get("path"),
            rank_int=data.get("rank_int") or None,
            overall_score=data.get("overall_score") or None,
        )
        db.add(uni)
        db.flush()  # get uni.id without committing

        # 2. detail_infors
        detail = data.get("detail") or {}
        di = DetailInfor(
            university_id=uni.id,
            fee=str(detail.get("fee")) if detail.get("fee") not in (None, "") else None,
            scholarship=detail.get("scholarship"),
            domestic=str(detail.get("domestic")) if detail.get("domestic") not in (None, "") else None,
            international=str(detail.get("international")) if detail.get("international") not in (None, "") else None,
            english_test=detail.get("english_test"),
            academic_test=detail.get("academic_test"),
            total_stu=str(detail.get("total_stu")) if detail.get("total_stu") not in (None, "") else None,
            ug_rate=str(detail.get("ug_rate")) if detail.get("ug_rate") not in (None, "") else None,
            pg_rate=str(detail.get("pg_rate")) if detail.get("pg_rate") not in (None, "") else None,
            inter_total=str(detail.get("inter_total")) if detail.get("inter_total") not in (None, "") else None,
            inter_ug_rate=str(detail.get("inter_ug_rate")) if detail.get("inter_ug_rate") not in (None, "") else None,
            inter_pg_rate=str(detail.get("inter_pg_rate")) if detail.get("inter_pg_rate") not in (None, "") else None,
        )
        db.add(di)

        # 3. entry_infor (degree_type 1 & 2)
        entry = data.get("entry") or {}
        for deg_str, vals in entry.items():
            deg = int(deg_str)
            ei = EntryInfor(
                university_id=uni.id,
                degree_type=deg,
                sat=vals.get("SAT") or None,
                act=vals.get("ACT") or None,
                gre=vals.get("GRE") or None,
                gmat=vals.get("GMAT") or None,
                atar=vals.get("ATAR") or None,
                gpa=vals.get("GPA") or None,
                toefl=vals.get("TOEFL") or None,
                ielts=vals.get("IELTS") or None,
            )
            db.add(ei)

        # 4. scores — flat dict {indicator_key: {score, rank}}
        from app.entities.score import Score as ScoreEntity
        scores_flat = data.get("scores") or {}
        for key, val in scores_flat.items():
            ind_id = UniversityModel._INDICATOR_MAP.get(key)
            if ind_id is None:
                continue
            sc_val = val.get("score") if isinstance(val, dict) else None
            rk_val = val.get("rank")  if isinstance(val, dict) else None
            if sc_val in (None, "") and rk_val in (None, ""):
                continue
            sc = ScoreEntity(
                university_id=uni.id,
                indicator_id=ind_id,
                score=float(sc_val) if sc_val not in (None, "") else None,
                rank_int=int(rk_val) if rk_val not in (None, "") else None,
            )
            db.add(sc)

        db.commit()
        db.refresh(uni)
        return {"id": uni.id, "name": uni.name}

    @staticmethod
    def get_edit_data(db: Session, university_id: int) -> dict:
        """Return entry_requirements + edit_scores in the format expected by the edit form."""
        # Entry requirements — all degree types
        entry_rows = (
            db.query(EntryInfor)
            .filter(EntryInfor.university_id == university_id)
            .all()
        )
        entry_requirements = [
            {
                "degree_type": ei.degree_type,
                "SAT":  ei.sat,   "ACT":  ei.act,
                "GRE":  ei.gre,   "GMAT": ei.gmat,
                "ATAR": ei.atar,  "GPA":  ei.gpa,
                "TOEFL": ei.toefl, "IELTS": ei.ielts,
            }
            for ei in entry_rows
        ]

        # Scores — reverse-map indicator_id → (cat_key, ind_key)
        reverse_map = {v: k for k, v in UniversityModel._INDICATOR_MAP.items()}
        cat_map = {
            "academic_reputation":    "research_discovery",
            "citations_per_faculty":  "research_discovery",
            "intl_research_network":  "research_discovery",
            "faculty_student_ratio":  "learning_experience",
            "employer_reputation":    "employability",
            "employment_outcomes":    "employability",
            "intl_student_ratio":     "global_engagement",
            "intl_faculty_ratio":     "global_engagement",
            "intl_student_diversity": "global_engagement",
            "sustainability_score":   "sustainability",
        }
        score_rows = (
            db.query(Score)
            .filter(Score.university_id == university_id)
            .all()
        )
        edit_scores: Dict[str, Any] = {}
        for sc in score_rows:
            ind_key = reverse_map.get(sc.indicator_id)
            if not ind_key:
                continue
            cat_key = cat_map.get(ind_key)
            if not cat_key:
                continue
            edit_scores.setdefault(cat_key, {})[ind_key] = {
                "score": sc.score,
                "rank":  sc.rank_int,
            }

        return {"entry_requirements": entry_requirements, "edit_scores": edit_scores}

    @staticmethod
    def get_ranking_scores(db: Session, university_id: int) -> List[Dict[str, Any]]:
        """Return ranking scores grouped by score_type category, each with indicator name, score, rank_int."""
        rows = (
            db.query(Score, Indicator, ScoreType)
            .join(Indicator, Score.indicator_id == Indicator.id)
            .join(ScoreType, Indicator.score_type_id == ScoreType.id)
            .filter(Score.university_id == university_id)
            .order_by(ScoreType.id.asc(), Indicator.id.asc())
            .all()
        )

        categories: Dict[str, list] = {}
        cat_order: List[str] = []
        for sc, ind, st in rows:
            cat = st.name
            if cat not in categories:
                categories[cat] = []
                cat_order.append(cat)
            categories[cat].append({
                "name":  ind.name,
                "score": sc.score,
                "rank":  sc.rank_int,
            })

        return [{"category": cat, "indicators": categories[cat]} for cat in cat_order]

    @staticmethod
    def update_university(db: Session, university_id: int, data: dict) -> dict:
        """Update university + related rows."""
        uni = db.query(University).filter(University.id == university_id).first()
        if not uni:
            return None

        for field in ("name", "city", "country_id", "logo", "path", "rank_int", "overall_score"):
            if field in data and data[field] not in ("", None) or (field in data and data[field] == False):
                setattr(uni, field, data[field] or None if field != "name" else data[field])

        # detail_infors
        detail = data.get("detail") or {}
        if detail:
            di = db.query(DetailInfor).filter(DetailInfor.university_id == university_id).first()
            if not di:
                di = DetailInfor(university_id=university_id)
                db.add(di)
            for field in ("fee", "scholarship", "domestic", "international", "english_test",
                          "academic_test", "total_stu", "ug_rate", "pg_rate",
                          "inter_total", "inter_ug_rate", "inter_pg_rate"):
                val = detail.get(field)
                if val not in (None, ""):
                    setattr(di, field, str(val) if field != "scholarship" else val)

        # entry_infor
        entry = data.get("entry") or {}
        for deg_str, vals in entry.items():
            deg = int(deg_str)
            ei = db.query(EntryInfor).filter(
                EntryInfor.university_id == university_id,
                EntryInfor.degree_type == deg
            ).first()
            if not ei:
                ei = EntryInfor(university_id=university_id, degree_type=deg)
                db.add(ei)
            for attr in ("SAT", "ACT", "GRE", "GMAT", "ATAR", "GPA", "TOEFL", "IELTS"):
                val = vals.get(attr)
                setattr(ei, attr.lower(), val or None)

        # scores
        from app.entities.score import Score as ScoreEntity
        scores_flat = data.get("scores") or {}
        for key, val in scores_flat.items():
            ind_id = UniversityModel._INDICATOR_MAP.get(key)
            if ind_id is None:
                continue
            sc_val = val.get("score") if isinstance(val, dict) else None
            rk_val = val.get("rank")  if isinstance(val, dict) else None
            sc = db.query(ScoreEntity).filter(
                ScoreEntity.university_id == university_id,
                ScoreEntity.indicator_id == ind_id
            ).first()
            if sc_val in (None, "") and rk_val in (None, ""):
                continue
            if not sc:
                sc = ScoreEntity(university_id=university_id, indicator_id=ind_id)
                db.add(sc)
            sc.score = float(sc_val) if sc_val not in (None, "") else None
            sc.rank_int = int(rk_val) if rk_val not in (None, "") else None

        db.commit()
        db.refresh(uni)
        return {"id": uni.id, "name": uni.name}

    @staticmethod
    def delete_university(db: Session, university_id: int) -> bool:
        """Delete a university by ID (cascades to related tables via FK ON DELETE CASCADE)."""
        uni = db.query(University).filter(University.id == university_id).first()
        if not uni:
            return False
        db.delete(uni)
        db.commit()
        return True
 