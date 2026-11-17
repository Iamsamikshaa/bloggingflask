import os
import secrets
from datetime import datetime, timedelta, timezone

from app.models import db, Category, Comment, Post, Tag, User
from app.models.category import slugify_text


def seed_database() -> bool:
    """Populate the database with sample categories, tags, authors, posts, and comments.

    Idempotent: exits early if posts already exist.
    Returns True if data was inserted, False if already seeded.
    """
    if Post.query.first() is not None:
        return False

    categories_data = [
        ("Engineering", "Software architecture, backend systems, and practical web engineering."),
        ("Architecture", "Spatial proportion, daylighting, and contemporary studio practice."),
        ("Design & Craft", "Typography, printmaking, tactile materials, and editorial form."),
        ("Urbanism", "Civic infrastructure, rail networks, and walkable public spaces."),
        ("Photography", "Analog workflows, optical craft, and documentary visual storytelling."),
    ]

    categories = {}
    for name, desc in categories_data:
        slug = slugify_text(name)
        cat = Category.query.filter_by(slug=slug).first()
        if cat is None:
            cat = Category(name=name, slug=slug, description=desc)
            db.session.add(cat)
        categories[slug] = cat

    tag_names = [
        "Flask",
        "Python",
        "SQLite",
        "Architecture",
        "Typography",
        "Craft",
        "Transit",
        "Film Photography",
    ]
    tags = {}
    for name in tag_names:
        slug = slugify_text(name)
        tag = Tag.query.filter_by(slug=slug).first()
        if tag is None:
            tag = Tag(name=name, slug=slug)
            db.session.add(tag)
        tags[slug] = tag

    seed_secret = os.environ.get("SEED_USER_PASSWORD") or secrets.token_urlsafe(16)

    authors_spec = [
        {
            "full_name": "Clara Vance",
            "username": "claravance",
            "email": "clara.vance@foliopress.example",
            "bio": "Principal systems architect and technical essayist exploring minimalist Python backends and durable web infrastructure.",
            "location": "Zurich, Switzerland",
            "website": "https://foliopress.example/authors/clara",
        },
        {
            "full_name": "Julian Mercer",
            "username": "julianmercer",
            "email": "julian.mercer@foliopress.example",
            "bio": "Architectural researcher and urbanist documenting civic transit halls, timber joinery, and daylight studies.",
            "location": "Berlin, Germany",
            "website": "https://foliopress.example/authors/julian",
        },
        {
            "full_name": "Elena Rostova",
            "username": "elenarostova",
            "email": "elena.rostova@foliopress.example",
            "bio": "Bookbinder, botanical archivist, and 35mm documentary photographer based in Edinburgh.",
            "location": "Edinburgh, UK",
            "website": "https://foliopress.example/authors/elena",
        },
    ]

    authors = {}
    for spec in authors_spec:
        user = User.query.filter_by(username=spec["username"]).first()
        if user is None:
            user = User(
                full_name=spec["full_name"],
                username=spec["username"],
                email=spec["email"],
                bio=spec["bio"],
                location=spec["location"],
                website=spec["website"],
            )
            user.set_password(seed_secret)
            db.session.add(user)
        authors[spec["username"]] = user

    db.session.flush()

    now = datetime.now(timezone.utc)

    posts_spec = [
        {
            "title": "Designing Studio Spaces Around Morning Light and Material Honesty",
            "slug": "designing-studio-spaces-around-morning-light",
            "description": "How north-facing glazing, raw timber tables, and deliberate acoustic calm transform everyday creative work.",
            "category": "architecture",
            "author": "julianmercer",
            "image": "images/post_architecture.jpg",
            "tags": ["architecture", "craft"],
            "days_ago": 1,
            "content": (
                "<p>Good architectural studios rarely announce themselves with theatrical gestures. "
                "Instead, they establish a quiet pact between daylight, proportion, and the tactile tools resting on the worktable.</p>"
                "<h2>Proportion Before Ornament</h2>"
                "<p>When sunlight enters across an oak drafting surface at an oblique angle, every elevation drawing and linen notebook "
                "gains depth. Rather than flooding a room with uniform overhead illumination, directional daylight creates natural focal zones "
                "for sketching, reading, and physical model making.</p>"
                "<blockquote>Light does not merely reveal a room; it gives weight and cadence to the hours spent inside it.</blockquote>"
                "<p>Three principles consistently anchor durable studio architecture:</p>"
                "<ul>"
                "<li><strong>Honest surface patina:</strong> Untreated hardwood and matte plaster age gracefully under daily use.</li>"
                "<li><strong>Deep window reveals:</strong> Angled sills soften glare while extending usable shelf space.</li>"
                "<li><strong>Acoustic separation:</strong> Heavy bookshelves and lime-washed masonry absorb chatter naturally.</li>"
                "</ul>"
                "<p>Even modest workspaces benefit from editing out visual clutter until only the essential instruments remain within reach.</p>"
            ),
        },
        {
            "title": "Why Modular Flask Blueprints Still Anchor Dependable Web Systems",
            "slug": "why-modular-flask-blueprints-anchor-dependable-systems",
            "description": "A pragmatic tour of application factories, SQLAlchemy constraints, and clean separation of concerns in Python web apps.",
            "category": "engineering",
            "author": "claravance",
            "image": "images/post_engineering.jpg",
            "tags": ["flask", "python", "sqlite"],
            "days_ago": 2,
            "content": (
                "<p>Modern web stacks frequently trade clarity for layers of configuration. Yet when building long-lived publishing tools, "
                "a disciplined Flask architecture using Blueprints and an explicit application factory remains remarkably resilient.</p>"
                "<h2>Separating Domain Boundaries</h2>"
                "<p>Grouping routes into focused blueprints—authentication, editorial posts, reader comments, and author profiles—keeps each module "
                "compact enough to audit in a single sitting. Combined with Flask-SQLAlchemy and Alembic migrations, schema evolution becomes "
                "predictable and repeatable across development and production environments.</p>"
                "<h2>Transactional Integrity with SQLite</h2>"
                "<p>Enabling <code>PRAGMA foreign_keys=ON</code> at connection time guarantees that cascading deletes and relational constraints "
                "behave identically in lightweight SQLite tests and production deployments.</p>"
                "<p>Clean boundaries never go out of fashion because maintainability is ultimately a human constraint, not a framework benchmark.</p>"
            ),
        },
        {
            "title": "Archival Paper, Oak-Gall Ink, and the Patience of Botanical Pressing",
            "slug": "archival-paper-oak-gall-ink-and-botanical-pressing",
            "description": "Inside an independent studio preserving regional flora on handmade rag sheets with traditional iron-gall inks.",
            "category": "design-craft",
            "author": "elenarostova",
            "image": "images/post_botanical.jpg",
            "tags": ["craft", "typography"],
            "days_ago": 4,
            "content": (
                "<p>Long before digital cataloging, field naturalists relied on cotton rag sheets, bone folders, and slow-drying plant inks "
                "to build enduring botanical records that remain legible centuries later.</p>"
                "<h2>Preparing the Specimen</h2>"
                "<p>Each fern frond or meadow stem is pressed between unbuffered blotters under weighted cedar boards for three weeks. "
                "Once moisture has departed evenly, fine linen tape secures the stem without obscuring delicate venation.</p>"
                "<blockquote>Paper remembers how carefully it was handled; hurried folds leave permanent tension across the grain.</blockquote>"
                "<p>Catalog labels are inscribed by hand using walnut and oak-gall inks, pairing taxonomic precision with understated editorial spacing.</p>"
            ),
        },
        {
            "title": "Civic Cathedrals of Steel and Glass: Reading Modern Rail Halls",
            "slug": "civic-cathedrals-of-steel-and-glass-rail-halls",
            "description": "How transparent vaulted concourses turn daily transit into legible, dignified public architecture.",
            "category": "urbanism",
            "author": "julianmercer",
            "image": "images/post_transit.jpg",
            "tags": ["transit", "architecture"],
            "days_ago": 6,
            "content": (
                "<p>Great railway stations serve as the living rooms of interconnected cities. At dawn, when cross-beams catch low amber sunlight, "
                "the engineering logic of long-span glass vaults becomes immediately clear to every passing commuter.</p>"
                "<h2>Wayfinding Without Noise</h2>"
                "<p>When structural spans orient travelers intuitively toward platforms and daylight, signage can stay restrained. "
                "Generous vertical volume reduces crowding stress and transforms routine departures into calm civic rituals.</p>"
                "<p>Investing in generous transit architecture signals that shared public space deserves the same rigor as private monuments.</p>"
            ),
        },
        {
            "title": "Reading Contact Sheets: What 35mm Film Teaches About Editing",
            "slug": "reading-contact-sheets-what-35mm-film-teaches",
            "description": "Slowing down with a 10x loupe, grease pencil, and black-and-white contact strips to sharpen visual judgment.",
            "category": "photography",
            "author": "elenarostova",
            "image": "images/post_photography.jpg",
            "tags": ["film-photography", "craft"],
            "days_ago": 8,
            "content": (
                "<p>A roll of thirty-six exposures imposes an invaluable rhythm. When every shutter press carries physical cost, "
                "observation precedes composition rather than following it.</p>"
                "<h2>The Discipline of the Loupe</h2>"
                "<p>Spread across a light table or matte stone bench, a silver-gelatin contact sheet reveals every hesitation and triumph in sequence. "
                "Circling only two or three frames per roll trains the eye to recognize authentic gesture over superficial polish.</p>"
                "<p>That same editorial restraint translates directly to prose: cut away the near-misses so the decisive frame can breathe.</p>"
            ),
        },
        {
            "title": "Editorial Typography on the Web: Measure, Leading, and Quiet Rhythm",
            "slug": "editorial-typography-on-the-web-measure-and-rhythm",
            "description": "Practical CSS rules for setting 65-character reading columns, balanced headlines, and crisp hierarchy.",
            "category": "design-craft",
            "author": "claravance",
            "image": "images/post_architecture.jpg",
            "tags": ["typography", "craft"],
            "days_ago": 10,
            "content": (
                "<p>Typography carries ninety percent of an editorial site's atmosphere before a reader notices a single color swatch. "
                "Restraint in line length and vertical spacing turns dense technical prose into an inviting page.</p>"
                "<h2>Respecting the 65-Character Measure</h2>"
                "<p>Eyes fatigue rapidly when forced to track across ultra-wide viewports. Constraining body columns to roughly 68 characters "
                "with generous 1.75 line-height creates effortless horizontal sweeps from line to line.</p>"
                "<p>Pair one expressive serif display face with a neutral body font, and reserve tabular numerals for dates and indexes.</p>"
            ),
        },
        {
            "title": "Zero-Downtime Schema Migrations with Flask-Migrate and Alembic",
            "slug": "zero-downtime-schema-migrations-with-flask-migrate",
            "description": "Structuring database revisions safely so relational models evolve cleanly from prototype to production.",
            "category": "engineering",
            "author": "claravance",
            "image": "images/post_engineering.jpg",
            "tags": ["flask", "python", "sqlite"],
            "days_ago": 12,
            "content": (
                "<p>Every successful application eventually outgrows its initial tables. Treating schema changes as version-controlled artifacts "
                "through Flask-Migrate protects both developer velocity and production data integrity.</p>"
                "<h2>Inspect Before Applying</h2>"
                "<p>Always review generated Alembic upgrade and downgrade functions before committing. Explicit index names and non-null defaults "
                "prevent subtle surprises when migrating live databases under Gunicorn.</p>"
            ),
        },
        {
            "title": "Walkable Neighborhoods and the Geometry of Human-Scale Streets",
            "slug": "walkable-neighborhoods-and-human-scale-streets",
            "description": "Why continuous sidewalks, mixed-use ground floors, and shade canopies create resilient urban vitality.",
            "category": "urbanism",
            "author": "julianmercer",
            "image": "images/post_transit.jpg",
            "tags": ["transit", "architecture"],
            "days_ago": 15,
            "content": (
                "<p>Neighborhoods feel welcoming when street width, building height, and ground-floor transparency align with walking speed. "
                "Every ten meters of active storefront or shaded bench invites unhurried civic life.</p>"
                "<p>Designing cities for people rather than throughput alone remains the highest-leverage sustainability choice available today.</p>"
            ),
        },
        {
            "title": "Hardening Authentication Flows with Werkzeug and Flask-Login",
            "slug": "hardening-authentication-flows-with-werkzeug-and-flask-login",
            "description": "Practical defenses including salted password hashing, CSRF protection, and safe redirect validation.",
            "category": "engineering",
            "author": "claravance",
            "image": "images/post_engineering.jpg",
            "tags": ["flask", "python"],
            "days_ago": 18,
            "content": (
                "<p>Authentication is foundational trust. Never store plaintext credentials, enforce CSRF tokens on every state-changing form, "
                "and validate post-login redirect targets so external open redirects remain impossible.</p>"
                "<p>Combining Flask-Login session protection with strict ownership checks on edit and delete routes keeps user content secure.</p>"
            ),
        },
    ]

    created_posts = {}
    for spec in posts_spec:
        created_at = now - timedelta(days=spec["days_ago"])
        post = Post(
            title=spec["title"],
            slug=spec["slug"],
            description=spec["description"],
            content=spec["content"],
            featured_image=spec["image"],
            is_published=True,
            created_at=created_at,
            updated_at=created_at,
            author=authors[spec["author"]],
            category=categories[spec["category"]],
            tags=[tags[t] for t in spec["tags"]],
        )
        db.session.add(post)
        created_posts[spec["slug"]] = post

    db.session.flush()

    comments_spec = [
        (
            "designing-studio-spaces-around-morning-light",
            "claravance",
            "The note about angled window reveals softening glare mirrors how much calmer north-facing rooms feel during long writing sessions.",
            10,
        ),
        (
            "designing-studio-spaces-around-morning-light",
            "elenarostova",
            "Completely agree—our bookbinding bench sits directly beneath a tall sash window and rarely needs artificial lighting until late afternoon.",
            6,
        ),
        (
            "why-modular-flask-blueprints-anchor-dependable-systems",
            "julianmercer",
            "Clean blueprint boundaries really shine once a project grows past five or six routes. Great reminder on SQLite foreign_keys PRAGMA too.",
            12,
        ),
        (
            "archival-paper-oak-gall-ink-and-botanical-pressing",
            "claravance",
            "There is something deeply grounding about physical paper records that outlast multiple generations of software formats.",
            4,
        ),
    ]

    for slug, username, body, hours_ago in comments_spec:
        comment = Comment(
            body=body,
            user_id=authors[username].id,
            post_id=created_posts[slug].id,
            created_at=now - timedelta(hours=hours_ago),
            updated_at=now - timedelta(hours=hours_ago),
        )
        db.session.add(comment)

    db.session.commit()
    return True
