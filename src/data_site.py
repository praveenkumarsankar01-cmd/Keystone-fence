"""Site-wide settings and content. Edit CONFIG to take the site live."""

CONFIG = dict(
    name="Keystone Fence & Deck Co.",
    short="Keystone Fence & Deck",
    phone="(469) 555-0148",          # 555-01xx is reserved for fiction; replace with the real line
    phone_e164="+14695550148",
    email="estimates@keystonefence.example",
    base_url="https://www.keystonefence.example",   # production domain: canonicals, sitemap, schema
    city="Plano", region="TX", region_name="Texas",
    hours=[("Mon–Fri", "7:00 am – 6:00 pm"), ("Saturday", "8:00 am – 2:00 pm"), ("Sunday", "Closed (storm calls by phone)")],
    hours_schema=[(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], "07:00", "18:00"), (["Saturday"], "08:00", "14:00")],

    # Search visibility. Keystone is a fictional company, so the site ships
    # noindex: real homeowners must not find it and send their details to a
    # business that doesn't exist. Flip to True only for a real business.
    index=False,

    # Lead delivery. Web3Forms (https://web3forms.com) emails each submission
    # to the address registered with the key. The key is designed to be public.
    form_endpoint="https://api.web3forms.com/submit",
    form_access_key="",               # paste the Web3Forms access key here

    ga4_id="",                         # e.g. G-XXXXXXXXXX — loads gtag + lead events when set
    gsc_verification="",               # Google Search Console HTML-tag verification code

    fictional=True,
    credit_name="Chennai Digital Team",
    credit_url="https://chennaidigitalteam.com",
)

HOME = dict(
    title="Keystone Fence & Deck Co. | Fence Company in Plano, TX",
    meta="Fencing, custom gates, decks and land clearing across Plano, Frisco, McKinney and North Dallas. Steel posts standard. Request a free on-site estimate.",
    eyebrow="Plano · Collin County · North Dallas",
    h1="Fences built to stay straight in Texas clay.",
    lede="Cedar, steel and iron fencing, custom gates, decks and land clearing across Plano, Frisco, McKinney and North Dallas. Every estimate starts with a walk of your property line — never a price guessed online.",
    proof=["Galvanized steel posts, standard", "Written, itemized estimates", "Texas811 locate on every job", "Fully insured crews"],
)

# Home-hero video. The files live in static/assets/media/; src/video.py renders
# the illustrated version, and real footage can replace it under the same names.
HERO_VIDEO = dict(
    mp4="site-walk.mp4", webm="site-walk.webm", poster="site-walk.webp", tag="Sheet 00 · Site walk",
    desc="Illustrated video: a homeowner and a Keystone estimator talk at the back fence line. "
         "The old leaning fence comes out, and a new board-on-board cedar fence on steel posts, with a walk gate, is drawn in.",
    transcript=[("Homeowner", "We want privacy out back — and a gate for the mower."),
                ("Keystone estimator", "Board-on-board cedar, on galvanized steel posts."),
                ("Homeowner", "Will it stay straight?"),
                ("Keystone estimator", "Footings go 3 ft deep. It'll stay straight.")],
)

WHY = dict(
    code="Field note",
    title="Why fences lean in North Texas — and how we stop it",
    body=[
        "Collin County sits on Blackland Prairie clay. It swells when it's wet and shrinks and cracks when it's dry, and that movement works on every fence post in the ground. A shallow footing loosens a little each season until the fence starts to lean.",
        "Wood posts make it worse: they rot right at grade, where the soil holds moisture against them. That's why so many fences look fine at the top and fail at the bottom.",
    ],
    points=[
        ("Galvanized steel posts", "Standard on our wood fences. They don't rot, termites ignore them, and they sit behind the boards."),
        ("Footings sized to the fence", "Depth set by height and soil — in our clay, we err deeper."),
        ("Crowned concrete", "The top of every footing is shaped to shed water away from the post."),
    ],
)

STEPS = [
    ("Request", "Send the form with a few photos, or call. We confirm a time to visit within one business day."),
    ("Walk the line", "We measure, check grade, drainage, utilities and HOA rules, and talk through options on site."),
    ("Written estimate", "An itemized estimate by email — materials, footage, gates and removal broken out. No pressure, no expiring price."),
    ("Build and walk-through", "We schedule, request Texas811 locates, build, clean up daily and walk the finished job with you."),
]

COMMITMENTS = [
    ("estimate", "Written, itemized estimates", "Every line on paper before work starts: footage, materials, gates, removal. The price we quote is the price you pay unless you change the scope."),
    ("post", "Steel posts as standard", "Galvanized steel posts on every wood fence we build, unless your HOA requires wood."),
    ("locate", "Texas811 before every hole", "Utility locates requested before we dig, and private lines marked with you on site."),
    ("clean", "A clean site every day", "Offcuts, packaging and spoil cleaned up daily, not just on the last day."),
    ("contact", "One point of contact", "The person who quotes your job is the person you call until it's finished."),
    ("warranty", "Workmanship warranty in writing", "Our workmanship is warrantied in writing, separate from manufacturers' material warranties."),
]

AUDIENCES = [
    ("Homeowners", "Backyard fences, gates and decks — explained plainly, priced in writing."),
    ("HOAs & managers", "Common-area fencing and entrances with scopes, COIs and completion photos."),
    ("Builders & GCs", "Lot clearing, fencing and outdoor structures phased to your construction schedule."),
    ("Commercial owners", "Perimeter, security and access control for sites, yards and offices."),
]

HOME_FAQS = [
    ("Do you give prices online?", "No. Fence and deck prices depend on footage, grade, access, gates and what's in the ground, so we walk your property first. The estimate is free and comes in writing."),
    ("What areas do you serve?", "Plano, Frisco, McKinney, Allen, Richardson, Prosper and surrounding North Dallas and Collin County cities."),
    ("Do you handle permits and HOA approval?", "We pull permits where your city requires them and provide drawings and specs for your HOA application."),
    ("How soon can you start?", "It depends on the season and materials. We give you a realistic start window with your estimate, and we keep you updated if anything moves."),
]

ABOUT = dict(
    title="About Keystone Fence & Deck Co. | Plano, TX Fence Company",
    meta="Keystone Fence & Deck Co. builds fences, gates, decks and outdoor structures across Collin County, starting from one rule: set the posts right.",
    h1="About Keystone Fence & Deck Co.",
    lede="A Plano fence and deck company named for the stone that holds an arch together.",
    story=[
        "In an arch, the keystone is the wedge at the top that locks every other stone in place. Take it out and the arch comes down. We think about fence posts the same way: they're the one part everything else depends on, so they're where we spend the most care.",
        "Keystone Fence & Deck Co. builds fences, gates, decks and outdoor structures, and clears land, across Collin County and North Dallas. We started with one rule — set the posts right — and built everything else around it: galvanized steel posts as standard, footings sized to the job, gates on steel frames, and decks framed to code before they're finished to look good.",
        "We work for homeowners, HOAs, property managers, builders and commercial owners. Whoever you are, the process is the same: we walk your property, you get an itemized written estimate, and the person who quoted your job is the person you call.",
    ],
    creds=[
        ("Insured", "General liability and workers' compensation. Certificates on request."),
        ("Permits", "Pulled wherever your city requires them, with inspections scheduled."),
        ("Utility safety", "Texas811 locates requested before every dig."),
        ("Warranty", "Written workmanship warranty on every installation."),
    ],
)

CITIES = [
    dict(slug="plano", name="Plano", county="Collin County",
      title="Fence & Deck Contractor in Plano, TX | Keystone Fence & Deck",
      meta="Cedar privacy fences on steel posts, gates, decks and repairs for Plano homes, from Willow Bend to Old Shepard Place. Free on-site estimates.",
      lede="Plano is home base. Much of our work here is replacing the original fences on 1980s and '90s homes — often along an alley — and building decks and covers for yards that finally get used.",
      intro=[
        "A lot of Plano's housing went up in the 1980s and 1990s, and many of those neighborhoods still have their original wood fences, or a patchwork of repairs on top of them. If your fence leans along the alley, has more replacement pickets than original ones, or wobbles when the wind picks up, the posts have probably rotted at grade.",
        "Many Plano homes back onto rear alleys, which shapes how a fence is built. The alley side takes knocks from trash trucks and has to stay clear of utility easements, and access for materials usually comes through the alley too. We plan around all of it during the estimate.",
      ],
      notes=[("Alley-loaded lots", "Rear fences on alley lots take abuse. We use steel posts and keep clear of the easement lines you point out."), ("HOA neighborhoods", "Many Plano neighborhoods set rules on height, style and stain. We supply specs for your application."), ("Permits", "Where the city requires a permit for your fence or deck, we pull it and schedule inspections."), ("Expansive clay", "Deeper footings and steel posts keep fences straight as the ground moves.")],
      neighborhoods=["Willow Bend", "Deerfield", "Hunters Glen", "Los Rios", "Old Shepard Place", "Legacy"],
      featured=["fencing/wood-privacy-fence", "repair/post-replacement", "gates/custom-walk-gates", "decks/patio-covers", "repair/fence-staining", "fencing/horizontal-slat-fence"],
      nearby=["richardson", "allen", "frisco"],
      faqs=[("Do you work in all of Plano?", "Yes, from east Plano to Legacy and everywhere between."), ("Can you replace a fence along my alley?", "Yes — alley fence replacement is one of our most common Plano jobs."), ("How soon can you visit for an estimate?", "Plano is our home base, so estimate visits are usually scheduled within a few days.")],
      zoom=11,
      ll=(33.0137, -96.6925),     # lat, lon of the OpenStreetMap place node (map pins)
      xy=(300, 250)),
    dict(slug="frisco", name="Frisco", county="Collin & Denton Counties",
      title="Fence & Deck Contractor in Frisco, TX | Keystone Fence & Deck",
      meta="Builder-fence replacement, HOA-ready cedar fences, pool barriers, composite decks and pergolas for Frisco homes. Free on-site estimates.",
      lede="Frisco's newer neighborhoods come with builder fences that are starting to show their age, HOA standards to meet, and big backyards ready for decks and covers.",
      intro=[
        "Much of Frisco was built in the last twenty-five years, and builder-grade fences — pine pickets on wood posts, set shallow — are reaching the point where they lean and grey. Upgrading to cedar on steel posts is one of the most common projects we do here.",
        "Master-planned communities in Frisco often have detailed HOA fence standards covering height, board style and stain color. We work from your HOA's guidelines and give you a spec sheet for approval before we order materials.",
      ],
      notes=[("Builder-fence replacement", "Shallow-set builder fences replaced on galvanized steel posts."), ("HOA standards", "Built to your HOA's published height, style and color rules, with specs for approval."), ("Pools and backyards", "Barrier fencing and covers for yards that add a pool later."), ("Expansive clay", "Footings set deep for soil that moves with the seasons.")],
      neighborhoods=["Starwood", "Phillips Creek Ranch", "Newman Village", "Richwoods", "Frisco Lakes", "Stonebriar"],
      featured=["fencing/wood-privacy-fence", "fencing/horizontal-slat-fence", "fencing/pool-fence", "decks/composite-decks", "decks/pergolas", "repair/fence-staining"],
      nearby=["prosper", "plano", "mckinney"],
      faqs=[("Will you meet my HOA's fence requirements?", "Yes. We work from your HOA guidelines and supply specs for approval."), ("Do you replace builder-installed fences?", "Often — usually with cedar pickets on galvanized steel posts."), ("Do you build pool fences in Frisco?", "Yes, to the barrier requirements the city enforces.")],
      zoom=11,
      ll=(33.1506, -96.8238),
      xy=(170, 170)),
    dict(slug="mckinney", name="McKinney", county="Collin County",
      title="Fence & Deck Contractor in McKinney, TX | Keystone Fence & Deck",
      meta="Fences for McKinney's historic district, Stonebridge Ranch and Craig Ranch HOAs, plus pipe and ranch fencing and driveway gates for acreage. Free estimates.",
      lede="From the historic district to Stonebridge Ranch and acreage on the edges of town, McKinney asks for more fence types than almost anywhere we work.",
      intro=[
        "McKinney mixes almost every kind of property we build for: historic homes near the downtown square, master-planned neighborhoods like Stonebridge Ranch and Craig Ranch, and larger lots toward the edges of town where pipe and ranch fencing make sense.",
        "In and around the historic district, exterior changes such as fences may need additional design review, so we talk through materials and styles that fit before you apply. In the master-planned communities, HOA standards usually govern height and stain. On acreage, it's all about braced corners and long, straight runs.",
      ],
      notes=[("Historic district", "Fences near downtown may need design review; we help you choose a compliant style."), ("Master-planned HOAs", "Stonebridge Ranch, Craig Ranch and others have standards we build to."), ("Acreage", "Clearing, pipe and ranch fencing with braced corners, and drive gates."), ("Expansive clay", "Deep footings and steel posts.")],
      neighborhoods=["Stonebridge Ranch", "Craig Ranch", "Tucker Hill", "Adriatica", "Historic District", "Trinity Falls"],
      featured=["fencing/wood-privacy-fence", "fencing/pipe-ranch-fence", "land-clearing/acreage-clearing", "gates/driveway-gates", "gates/automatic-gate-openers", "decks/wood-decks"],
      nearby=["allen", "frisco", "prosper"],
      faqs=[("Can you build a fence in McKinney's historic district?", "Yes. Design review may apply, and we help you pick a style that fits before you apply."), ("Do you install ranch fencing around McKinney?", "Yes — pipe and ranch fencing with braced corners for acreage."), ("Do you automate driveway gates?", "Yes, swing and slide operators with safety devices.")],
      zoom=11,
      ll=(33.1976, -96.6154),
      xy=(395, 125)),
    dict(slug="allen", name="Allen", county="Collin County",
      title="Fence & Deck Contractor in Allen, TX | Keystone Fence & Deck",
      meta="Fence replacement, steel post upgrades, staining and deck repair for Allen's established neighborhoods, including shared backyard fences. Free estimates.",
      lede="Allen's 1990s and 2000s neighborhoods are where original fences are reaching the end of their life — and where a straight new fence lifts the whole street.",
      intro=[
        "Allen grew fast through the 1990s and 2000s, and many homes still have the fences they were built with. Twenty-odd years of North Texas sun and clay is about what a wood fence on wood posts can take, which is why fence replacement and post replacement are our most common Allen jobs.",
        "Many Allen neighborhoods share fences between backyards, so replacement often means working with a neighbor. We can quote the shared run so both households see the same scope, and build board-on-board or shadowbox so both sides look finished.",
      ],
      notes=[("Aging original fences", "Fences from the original build failing at the posts — replaced or re-posted."), ("Shared fences", "One scope for both neighbors, in two-sided styles."), ("HOA rules", "Built to HOA height and color standards."), ("Expansive clay", "Deeper footings and steel posts.")],
      neighborhoods=["Twin Creeks", "Star Creek", "Montgomery Farm", "Bethany Lakes", "Watters Crossing"],
      featured=["fencing/wood-privacy-fence", "repair/post-replacement", "repair/fence-repair", "repair/fence-staining", "land-clearing/site-grading", "gates/custom-walk-gates"],
      nearby=["plano", "mckinney", "richardson"],
      faqs=[("Can you quote a shared fence for my neighbor and me?", "Yes — one scope for the shared run so each household sees the same thing."), ("Should I repair or replace my original fence?", "If the posts are the problem and the pickets are sound, re-posting can save money. We'll tell you honestly."), ("Do you stain fences in Allen?", "Yes, in HOA-approved colors.")],
      zoom=12,
      ll=(33.1032, -96.6706),
      xy=(360, 195)),
    dict(slug="richardson", name="Richardson", county="Dallas & Collin Counties",
      title="Fence & Deck Contractor in Richardson, TX | Keystone Fence & Deck",
      meta="Fence replacement and repair around mature trees and alley lots, storm repairs, decks and pergolas for Richardson's established neighborhoods.",
      lede="Richardson's established neighborhoods mean mature trees, alley lots and older fences — and a lot of careful work around roots and utilities.",
      intro=[
        "Much of Richardson was built from the 1950s through the 1970s, and its neighborhoods have the mature trees to show for it. Big trees near fence lines bring their own challenges: roots where posts need to go, limbs that drop in storms, and shade that keeps fences damp.",
        "Many Richardson homes have rear alleys and older utility lines, so we're careful where we dig. We request utility locates before every job, hand-dig near large roots, and adjust post spacing to work around them rather than cutting major roots.",
      ],
      notes=[("Mature trees", "Hand-digging near roots and adjusting post spacing instead of cutting major roots."), ("Alley lots", "Alley-side fences built to take wear and stay clear of easements."), ("Older fences", "Replacement and repair for decades-old fences."), ("Storm limbs", "Tree-strike repairs, coordinated with tree services.")],
      neighborhoods=["Canyon Creek", "Richardson Heights", "Prairie Creek", "Cottonwood Heights"],
      featured=["fencing/wood-privacy-fence", "repair/storm-damage-fence-repair", "repair/fence-repair", "decks/wood-decks", "decks/pergolas", "gates/gate-repair"],
      nearby=["plano", "allen"],
      faqs=[("Can you build a fence near a large tree?", "Yes. We hand-dig near roots and adjust post spacing to avoid cutting major roots."), ("Do you repair fences hit by falling limbs?", "Yes, and we coordinate with tree services for large limbs."), ("Do you replace alley fences?", "Yes, regularly.")],
      zoom=12,
      ll=(32.9482, -96.7297),
      xy=(330, 320)),
    dict(slug="prosper", name="Prosper", county="Collin & Denton Counties",
      title="Fence & Deck Contractor in Prosper, TX | Keystone Fence & Deck",
      meta="Fences for new construction and large lots, pipe and ranch fencing, automatic driveway gates and patio covers across Prosper. Free on-site estimates.",
      lede="Prosper's large new lots and acreage call for long fence runs, automated driveway gates and outdoor spaces built from scratch.",
      intro=[
        "Prosper is one of the fastest-growing towns in the area, with new master-planned neighborhoods and larger lots than most of Collin County. That means new fences on new construction, long runs along back property lines, and driveways long enough to want an automatic gate.",
        "New construction has its own considerations: fresh fill soil that settles, final grading that changes the line, and HOA approvals that must happen before materials are ordered. We time our work around your builder and set footings for soil that's still settling.",
      ],
      notes=[("New construction", "Coordinated with builders, with footings set for settling fill."), ("Large lots", "Fence lines cleared and long runs priced efficiently, with braced corners."), ("Driveway gates", "Automatic gates for long drives — solar where power is far away."), ("HOA approvals", "Specs ready for your HOA before we order.")],
      neighborhoods=["Windsong Ranch", "Star Trail", "Whitley Place", "Lakes of Prosper"],
      featured=["fencing/wood-privacy-fence", "fencing/wrought-iron-fence", "fencing/pipe-ranch-fence", "land-clearing/fence-line-clearing", "gates/driveway-gates", "gates/automatic-gate-openers"],
      nearby=["frisco", "mckinney"],
      faqs=[("Can you install a fence soon after closing?", "Yes — we schedule around your builder's final grading and your HOA approval."), ("Do you install solar gate openers?", "Yes, useful on long drives where running power is costly."), ("Do you build fences on acreage?", "Yes, pipe and ranch fencing with braced corners.")],
      zoom=12,
      ll=(33.2372, -96.7977),
      xy=(200, 75)),
]

ALSO_SERVING = ["Dallas", "Carrollton", "The Colony", "Little Elm", "Celina", "Fairview", "Lucas", "Parker", "Murphy", "Wylie", "Garland"]

# Typical project scopes. These describe what a job of each kind involves;
# they are not claims about specific completed jobs. Replace with real,
# photographed projects when the site represents a real business.
PROJECTS = [
    dict(silo="fencing", code="F-01", drawing="board_on_board", title="Alley fence replacement on steel posts", where="Plano · alley-loaded lot", who="Homeowner",
         spec=[("Length", "140 LF"), ("Height", "8'-0\""), ("Style", "Board-on-board cedar, cap and trim"), ("Posts", "Galvanized steel"), ("Gates", "1 walk, 1 double"), ("Typical duration", "3 days")],
         story="An original 1990s fence leaning along the alley: torn out, re-posted in steel and rebuilt in cedar with a double gate for bins."),
    dict(silo="fencing", code="F-02", drawing="horizontal", title="Modern horizontal front screen", where="Frisco · corner lot", who="Homeowner",
         spec=[("Length", "64 LF"), ("Height", "6'-0\""), ("Style", "1x6 cedar, 3/8\" gap"), ("Posts", "2x2 black steel"), ("Gates", "1 walk"), ("Typical duration", "2 days")],
         story="A street-facing screen for a corner lot, with a matching gate and the cedar sealed on day one."),
    dict(silo="fencing", code="F-05", drawing="pool", title="Pool barrier for a new pool", where="Prosper · new construction", who="Homeowner + pool builder",
         spec=[("Length", "180 LF"), ("Height", "5'-0\""), ("Style", "Powder-coated aluminum"), ("Gates", "2 self-closing, self-latching"), ("Posts", "Core-drilled into deck"), ("Typical duration", "2 days")],
         story="Barrier scheduled ahead of the final pool inspection, with posts grouted into the new deck."),
    dict(silo="fencing", code="F-03", drawing="iron", title="HOA common-area perimeter", where="McKinney · master-planned community", who="HOA / property manager",
         spec=[("Length", "900 LF"), ("Height", "6'-0\""), ("Style", "Ornamental steel, racked on slope"), ("Paperwork", "COI and completion photos"), ("Phasing", "Around resident access"), ("Typical duration", "6 days")],
         story="A long run along a greenbelt, racked to follow the slope and phased so the trail stayed open."),
    dict(silo="fencing", code="F-04", drawing="pipe", title="Pasture pipe fence with H-braces", where="Collin County acreage", who="Landowner",
         spec=[("Length", "1,600 LF"), ("Height", "4'-6\""), ("Style", "3-rail welded pipe + welded wire"), ("Corners", "4 H-braces"), ("Gates", "1 ranch gate"), ("Typical duration", "8 days")],
         story="Fencing for horses on acreage, laid out from survey pins with braced corners at every turn."),
    dict(silo="gates", code="G-01", drawing="driveway_gate", title="Arched drive gate with solar operator", where="Prosper · long driveway", who="Homeowner",
         spec=[("Opening", "16'-0\""), ("Gate", "Double-swing steel, arched"), ("Operator", "Solar with battery backup"), ("Access", "Keypad on gooseneck"), ("Safety", "Photo eyes"), ("Typical duration", "3 days")],
         story="An entrance gate far from power, run on solar, with a keypad set at driver's-window height."),
    dict(silo="gates", code="G-04", drawing="access", title="HOA entrance access upgrade", where="Allen · neighborhood entrance", who="HOA",
         spec=[("Scope", "Keypad to cellular intercom"), ("Users", "Multi-unit codes"), ("Exit", "Vehicle exit loop"), ("Safety", "Photo eyes replaced"), ("Training", "Board and manager"), ("Typical duration", "2 days")],
         story="An aging keypad replaced with a multi-user cellular intercom that the board can manage from a phone."),
    dict(silo="gates", code="G-05", drawing="gate_repair", title="Sagging side gate rebuilt on steel", where="Richardson · side yard", who="Homeowner",
         spec=[("Gate", "4'-0\" walk gate"), ("Fix", "Rebuilt on welded steel frame"), ("Post", "Hinge post reset in concrete"), ("Hardware", "New hinges and latch"), ("Boards", "Existing cedar reused"), ("Typical duration", "1 day")],
         story="A gate that hadn't latched in a year, rebuilt on a steel frame using the original boards."),
    dict(silo="decks", code="D-01", drawing="wood_deck", title="Raised cedar deck with stairs", where="Allen · sloped backyard", who="Homeowner",
         spec=[("Size", "16' x 20' (320 sq ft)"), ("Height", "3'-0\" above grade"), ("Decking", "Cedar"), ("Guard", "36\" cedar railing"), ("Stairs", "4 risers"), ("Typical duration", "8 days")],
         story="A deck stepping off the back door over a falling yard, permitted and inspected."),
    dict(silo="decks", code="D-03", drawing="pergola", title="Pergola over a composite deck", where="Frisco · west-facing yard", who="Homeowner",
         spec=[("Deck", "12' x 14' capped composite"), ("Pergola", "12' x 12' cedar"), ("Shade", "Tight purlin spacing"), ("Footings", "Concrete piers"), ("Extras", "Fan and light prep"), ("Typical duration", "7 days")],
         story="Afternoon shade for a west-facing yard, with a lighter composite color chosen to stay cooler."),
    dict(silo="repair", code="R-02", drawing="storm", title="Storm rebuild after straight-line winds", where="Richardson · mature trees", who="Homeowner (insurance claim)",
         spec=[("Section", "48 LF"), ("Posts", "6 replaced in steel"), ("Boards", "Matched cedar"), ("Docs", "Dated photos and written scope"), ("Securing", "Same-day temporary panels"), ("Typical duration", "1 + 2 days")],
         story="A yard with dogs secured the same day, then rebuilt on steel posts once the claim was approved."),
    dict(silo="repair", code="R-04", drawing="post_section", title="Re-post and stain instead of replace", where="Plano · original fence", who="Homeowner",
         spec=[("Posts", "22 replaced in steel"), ("Boards", "Existing, re-fastened"), ("Stain", "Semi-transparent, both sides"), ("Length", "210 LF"), ("Saved", "The boards"), ("Typical duration", "3 days")],
         story="Sound boards on rotted posts: re-posted in steel and stained, for far less than a new fence."),
    dict(silo="land-clearing", code="L-05", drawing="mulching", title="Forestry mulching on overgrown acreage", where="McKinney · 5 acres", who="Landowner",
         spec=[("Area", "5 acres"), ("Vegetation", "Privet, cedar, saplings"), ("Keepers", "14 oaks and pecans flagged"), ("Method", "Mulched in place"), ("Burning", "None"), ("Typical duration", "4 days")],
         story="A pasture lost to privet and cedar opened back up, with the mature oaks and pecans flagged and left standing."),
    dict(silo="land-clearing", code="L-04", drawing="fence_line", title="Fence line cleared, then fenced", where="Prosper area · acreage", who="Landowner",
         spec=[("Line", "2,400 LF"), ("Strip", "12 ft cleared"), ("Old fence", "Wire and T-posts pulled"), ("Pins", "Located from survey"), ("Then", "Pipe fence, same crew"), ("Typical duration", "3 + 6 days")],
         story="A buried boundary cleared, the old wire pulled, and a new pipe fence built on the line by the same crew."),
    dict(silo="land-clearing", code="L-06", drawing="grading", title="Backyard regrade before a deck", where="Allen · water toward the house", who="Homeowner",
         spec=[("Area", "1,100 sq ft"), ("Fall", "6 in. in the first 10 ft"), ("Fill", "Compacted in lifts"), ("Pad", "Deck area leveled"), ("Finish", "Ready for sod"), ("Typical duration", "2 days")],
         story="Water pooling at the slab corrected with a regrade, and a level pad left ready for the new deck."),
]
