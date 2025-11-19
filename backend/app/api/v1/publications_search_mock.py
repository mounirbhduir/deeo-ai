"""
Mock endpoint for advanced publication search (Phase 4 - Frontend demo).

This module provides a mock search endpoint with realistic data for the frontend
publication search page. It simulates advanced filtering, sorting, and pagination
without requiring database queries.
"""

from fastapi import APIRouter, Query
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import random

router = APIRouter()

# Mock data - realistic AI publication titles
PUBLICATION_TITLES = [
    "Deep Learning for Image Recognition and Classification",
    "Natural Language Processing with Transformer Architectures",
    "Reinforcement Learning Applications in Autonomous Robotics",
    "Graph Neural Networks: A Comprehensive Survey",
    "Zero-Shot and Few-Shot Learning Classification Methods",
    "Attention Mechanisms in Modern Neural Network Architectures",
    "Few-Shot Learning Approaches for Computer Vision",
    "Generative Adversarial Networks for Image Synthesis",
    "Meta-Learning Strategies for Fast Adaptation",
    "Transfer Learning Techniques in Deep Neural Networks",
    "Contrastive Learning for Self-Supervised Representation",
    "Vision Transformers for Image Understanding",
    "Large Language Models: Training and Fine-tuning",
    "Diffusion Models for Generative AI Applications",
    "Neural Architecture Search and AutoML",
    "Explainable AI: Interpretability in Deep Learning",
    "Multimodal Learning: Vision and Language Integration",
    "Edge AI: Efficient Neural Networks for Mobile Devices",
    "Federated Learning for Privacy-Preserving AI",
    "Continual Learning and Catastrophic Forgetting",
]

ORGANIZATIONS = [
    "MIT Computer Science and AI Laboratory",
    "Stanford Artificial Intelligence Laboratory",
    "DeepMind Technologies",
    "OpenAI Research",
    "Google Brain",
    "Facebook AI Research (FAIR)",
    "Microsoft Research AI",
    "UC Berkeley AI Research",
    "Carnegie Mellon University",
    "ETH Zürich",
]

THEMES_DATA = [
    {"id": "theme-ml", "label": "Machine Learning"},
    {"id": "theme-nlp", "label": "Natural Language Processing"},
    {"id": "theme-cv", "label": "Computer Vision"},
    {"id": "theme-rl", "label": "Reinforcement Learning"},
    {"id": "theme-dl", "label": "Deep Learning"},
    {"id": "theme-gnn", "label": "Graph Neural Networks"},
    {"id": "theme-genai", "label": "Generative AI"},
]

PUBLICATION_TYPES = ["article", "preprint", "conference_paper", "journal_paper", "thesis"]

# Real author data for consistency with authors_mock.py
REAL_AUTHORS = [
    {"id": "author-001", "nom": "Bengio", "prenom": "Yoshua"},
    {"id": "author-002", "nom": "LeCun", "prenom": "Yann"},
    {"id": "author-003", "nom": "Hinton", "prenom": "Geoffrey"},
    {"id": "author-004", "nom": "Schmidhuber", "prenom": "Jürgen"},
    {"id": "author-005", "nom": "Ng", "prenom": "Andrew"},
    {"id": "author-006", "nom": "Goodfellow", "prenom": "Ian"},
    {"id": "author-007", "nom": "Sutskever", "prenom": "Ilya"},
    {"id": "author-008", "nom": "Silver", "prenom": "David"},
    {"id": "author-009", "nom": "Vaswani", "prenom": "Ashish"},
    {"id": "author-010", "nom": "Devlin", "prenom": "Jacob"},
    {"id": "author-011", "nom": "Radford", "prenom": "Alec"},
    {"id": "author-012", "nom": "Manning", "prenom": "Christopher"},
    {"id": "author-013", "nom": "He", "prenom": "Kaiming"},
    {"id": "author-014", "nom": "Ren", "prenom": "Shaoqing"},
    {"id": "author-015", "nom": "Fei-Fei", "prenom": "Li"},
    {"id": "author-016", "nom": "Abbeel", "prenom": "Pieter"},
    {"id": "author-017", "nom": "Levine", "prenom": "Sergey"},
    {"id": "author-018", "nom": "Schulman", "prenom": "John"},
    {"id": "author-019", "nom": "Bronstein", "prenom": "Michael"},
    {"id": "author-020", "nom": "Kipf", "prenom": "Thomas"},
    {"id": "author-021", "nom": "Finn", "prenom": "Chelsea"},
    {"id": "author-022", "nom": "Vinyals", "prenom": "Oriol"},
    {"id": "author-023", "nom": "Ho", "prenom": "Jonathan"},
    {"id": "author-024", "nom": "Song", "prenom": "Yang"},
    {"id": "author-025", "nom": "Zoph", "prenom": "Barret"},
    {"id": "author-026", "nom": "Le", "prenom": "Quoc V."},
    {"id": "author-027", "nom": "Ribeiro", "prenom": "Marco Tulio"},
    {"id": "author-028", "nom": "Kim", "prenom": "Been"},
    {"id": "author-029", "nom": "Ramesh", "prenom": "Aditya"},
    {"id": "author-030", "nom": "Chen", "prenom": "Ting"},
]

# Generate 50 mock publications
MOCK_PUBLICATIONS: List[Dict[str, Any]] = []

for i in range(50):
    title_idx = i % len(PUBLICATION_TITLES)
    title = PUBLICATION_TITLES[title_idx]

    # Random authors from REAL_AUTHORS list (1-5 per publication)
    num_authors = random.randint(1, 5)
    auteurs = random.sample(REAL_AUTHORS, num_authors)

    # Random organizations (1-3)
    num_orgs = random.randint(1, 3)
    organisations = [
        {
            "id": f"org-{i}-{j}",
            "nom": random.choice(ORGANIZATIONS)
        }
        for j in range(num_orgs)
    ]

    # Random themes (1-4)
    num_themes = random.randint(1, 4)
    themes = random.sample(THEMES_DATA, num_themes)

    # Random publication type
    pub_type = random.choice(PUBLICATION_TYPES)

    # Random date within last 2 years
    days_ago = random.randint(1, 730)
    pub_date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")

    # Random citations (exponential distribution, weighted towards lower numbers)
    citations = int(random.expovariate(0.01)) if random.random() > 0.1 else random.randint(0, 50)
    citations = min(citations, 1000)

    # Generate valid arXiv ID (YYMM.NNNNN format)
    # Use the publication date to determine month
    pub_datetime = datetime.strptime(pub_date, "%Y-%m-%d")
    arxiv_year = pub_datetime.strftime("%y")  # 2-digit year
    arxiv_month = pub_datetime.strftime("%m")  # 2-digit month
    arxiv_number = f"{10000+i:05d}"  # 5-digit number
    valid_arxiv_id = f"{arxiv_year}{arxiv_month}.{arxiv_number}"

    publication = {
        "id": f"pub-{i:03d}",
        "titre": f"{title}",
        "abstract": (
            f"This comprehensive study explores {title.lower()}. "
            f"We present novel approaches and methodologies that advance the state-of-the-art "
            f"in artificial intelligence and machine learning. Our experimental results demonstrate "
            f"significant improvements over existing baselines across multiple benchmark datasets. "
            f"The proposed framework shows promise for real-world applications and opens new "
            f"directions for future research in this domain."
        ),
        "doi": f"10.1234/deeo.2024.{1000+i}" if random.random() > 0.3 else None,
        "arxiv_id": valid_arxiv_id if random.random() > 0.4 else None,  # Valid format: YYMM.NNNNN
        "date_publication": pub_date,
        "type_publication": pub_type,
        "nombre_citations": citations,
        "auteurs": auteurs,
        "organisations": organisations,
        "themes": themes,
    }

    MOCK_PUBLICATIONS.append(publication)


@router.get("/search")
async def search_publications(
    q: Optional[str] = Query(None, description="Full-text search query"),
    theme: Optional[str] = Query(None, description="Theme filter"),
    type: Optional[str] = Query(None, description="Publication type filter"),
    organization: Optional[str] = Query(None, description="Organization filter"),
    date_from: Optional[str] = Query(None, description="Date from (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="Date to (YYYY-MM-DD)"),
    sort_by: str = Query("date", description="Sort by field (date|citations|relevance)"),
    sort_order: str = Query("desc", description="Sort order (asc|desc)"),
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
) -> Dict[str, Any]:
    """
    Advanced publication search with filters (MOCK DATA for frontend demo).

    This endpoint returns mock data for demonstrating the frontend search functionality.

    **Filters:**
    - **q**: Full-text search in title and abstract
    - **theme**: Filter by theme (e.g., "Machine Learning", "NLP")
    - **type**: Filter by publication type (article, preprint, etc.)
    - **organization**: Filter by organization name (partial match)
    - **date_from/date_to**: Date range filter (YYYY-MM-DD format)

    **Sorting:**
    - **sort_by**: Sort by date, citations, or relevance
    - **sort_order**: asc or desc

    **Pagination:**
    - **page**: Page number (1-based, default: 1)
    - **limit**: Items per page (max 100, default: 20)

    **Returns:**
    ```json
    {
      "items": [...],
      "total": 50,
      "page": 1,
      "limit": 20,
      "total_pages": 3
    }
    ```
    """

    # Start with all publications
    filtered = MOCK_PUBLICATIONS.copy()

    # Apply full-text search
    if q:
        q_lower = q.lower()
        filtered = [
            p for p in filtered
            if q_lower in p["titre"].lower() or q_lower in p["abstract"].lower()
        ]

    # Apply theme filter (by theme ID)
    if theme:
        filtered = [
            p for p in filtered
            if any(t["id"] == theme for t in p["themes"])
        ]

    # Apply type filter
    if type:
        filtered = [
            p for p in filtered
            if p["type_publication"] == type
        ]

    # Apply organization filter (partial match)
    if organization:
        org_lower = organization.lower()
        filtered = [
            p for p in filtered
            if any(org_lower in o["nom"].lower() for o in p["organisations"])
        ]

    # Apply date range filters
    if date_from:
        filtered = [
            p for p in filtered
            if p["date_publication"] >= date_from
        ]

    if date_to:
        filtered = [
            p for p in filtered
            if p["date_publication"] <= date_to
        ]

    # Sort publications
    reverse = (sort_order == "desc")

    if sort_by == "date":
        filtered.sort(key=lambda p: p["date_publication"], reverse=reverse)
    elif sort_by == "citations":
        filtered.sort(key=lambda p: p["nombre_citations"], reverse=reverse)
    elif sort_by == "relevance":
        # For relevance, use citations as a proxy (in real app, would use search score)
        filtered.sort(key=lambda p: p["nombre_citations"], reverse=True)

    # Calculate pagination
    total = len(filtered)
    total_pages = (total + limit - 1) // limit if total > 0 else 1

    # Validate page number
    if page > total_pages and total > 0:
        page = total_pages

    # Apply pagination
    start = (page - 1) * limit
    end = start + limit
    items = filtered[start:end]

    return {
        "items": items,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
    }


@router.get("/search/{publication_id}")
async def get_publication_by_id(publication_id: str) -> Dict[str, Any]:
    """
    Get a single publication by ID (MOCK DATA).

    **Parameters:**
    - **publication_id**: Publication ID (e.g., "pub-001")

    **Returns:**
    Publication details

    **Raises:**
    - 404: Publication not found
    """
    from fastapi import HTTPException

    pub = next((p for p in MOCK_PUBLICATIONS if p["id"] == publication_id), None)

    if not pub:
        raise HTTPException(
            status_code=404,
            detail=f"Publication with ID '{publication_id}' not found"
        )

    return pub
