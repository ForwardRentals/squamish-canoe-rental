#!/usr/bin/env python3
"""Build one canoe-rental page per lake/river + the /canoe-rental-locations/ hub.

One template, one data entry per place. Nav and footer are sliced from
echo-lake-canoe-rental/index.html so the pages match the hand-built ones.

RULE: reviews must be real Google reviews already on the site, quoted exactly,
attached only to the place they mention. Never invent them. Pages without a
matching review get no review section.

Run:  python3 scripts/build_locations.py
"""
import html, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://squamishcanoerental.com"
BOOK = "https://rentedlocal.com/Profile?userId=698a2b3bca1e37a683b7bfeb"
SRC = (ROOT / "echo-lake-canoe-rental/index.html").read_text()
NAV = SRC[SRC.index("  <nav class=\"navbar\""):SRC.index("  <header class=\"hero\"")]
FOOTER = SRC[SRC.index("  <footer class=\"footer\">"):SRC.index("</body>")]

REVIEWS = {
    "caroline": ("Caroline Guimond", "I rented 1 canoe and 4 paddle boards for the day. Fantastic customer service. The equipment was in great shape and worked well. They dropped it all off at Brohm Lake for a very reasonable price. Would recommend 100%!"),
    "james": ("James", "An all round incredible experience. Took a 3 person canoe down the Squamish River from the Ashlu FSR bridge to around the Squamish Estuary and into the Mamquam Blind. River level was perfect for the journey. No major rapids."),
    "zoe": ("Zoe Yanik", "Had an absolute blast canoeing here! Jeremy was super helpful and made the process quick and easy. We launched from the Squamish boat launch and paddled into the river a bit. Got some good views and even some seals playing around in the river!"),
    "axel": ("Axel Runner", "I rented a canoe from Jeremy last weekend for a day trip up the Squamish River. The canoe was in excellent condition, handled the water extremely well and was a great experience overall! If you&rsquo;re looking for a good canoe rental in Squamish I would 10/10 recommend this service to anyone!"),
    "peter": ("Peter Allen", "We had an incredible day renting boats from Jeremy, he gave us everything we needed including paddles and lifejackets. Communication was super easy and he gave us awesome recommendations of where to paddle on the Squamish River!"),
    "ocelab": ("Ocelab", "We had an absolutely lovely afternoon canoeing on the Howe Sound, thanks to Jeremy who was wonderful, professional and accommodating. I highly recommend this rental company. Thank you!"),
}

# level: Beginner / Beginner-Intermediate / Intermediate. area: Squamish|Whistler|Pemberton
PLACES = [
    dict(slug="alice-lake-canoe-rental", name="Alice Lake", area="Squamish", level="Beginner",
         lat=49.7776, lon=-123.1206, img="lake-canoe.jpg",
         title="Alice Lake Canoe Rental | Delivered to Your Campsite or Beach",
         desc="Canoe rental at Alice Lake Provincial Park, Squamish. We deliver to your campsite or the day-use area. Calm, family-friendly water, up to 3 paddlers, all gear included.",
         hook="Four lakes, one park and a campground. We bring the canoe to your campsite or the beach so you skip the roof rack and the parking scramble.",
         intro=["Alice Lake Provincial Park sits just north of downtown Squamish, with four small lakes, sandy beaches and one of the busiest campgrounds in the Sea to Sky. Alice Lake itself is calm, sheltered and warm by midsummer, which makes it about as easy as canoeing gets.",
                "It's also our most popular multi-day delivery. Families book a canoe for the length of their camping stay, we drop it at the site, and the kids paddle every morning before the beach gets busy. Day visitors get the same service at the day-use area."],
         best="Families, first-time paddlers, campers and dogs",
         tips=["Paddle early. Summer weekends get busy on the beaches by late morning, but the water stays roomy.",
               "Book the full camping stay so the canoe is there whenever you want it. We pick up on check-out day.",
               "Pair the paddle with the Four Lakes Trail loop for a full park day."],
         faqs=[("Can you deliver a canoe to my Alice Lake campsite?", "Yes. Campsite delivery is our most popular Alice Lake booking. Give us your site number and dates, and we'll drop off and pick up at the site."),
               ("Is Alice Lake good for beginners?", "It's one of the best beginner lakes in Squamish: small, sheltered and calm, with no current or tide to deal with."),
               ("Can I bring my dog in the canoe?", "Yes. Dogs are welcome in our canoes. Check the park's current pet rules for beaches and trails.")],
         reviews=[], related=["brohm-lake-canoe-rental", "cat-lake-canoe-rental", "browning-lake-canoe-rental"]),
    dict(slug="brohm-lake-canoe-rental", name="Brohm Lake", area="Squamish", level="Beginner",
         lat=49.8297, lon=-123.1338, img="red-canoe-open.jpg",
         title="Brohm Lake Canoe Rental Squamish | Canoes & SUPs Delivered",
         desc="Canoe and paddleboard rental delivered to Brohm Lake, north of Squamish. Warm summer water, cliffs and a shoreline trail. Up to 3 paddlers per canoe, gear included.",
         hook="A warm summer lake with cliffs, swim spots and a shoreline trail, 15 minutes north of Squamish. We deliver to the launch.",
         intro=["Brohm Lake sits right off the Sea to Sky Highway north of Squamish, inside an interpretive forest with a trail all the way around the shore. By July it's one of the warmest lakes in the area, and the rocky edges make it a classic hot-day swim-and-paddle spot.",
                "A canoe opens up the quieter corners of the lake, away from the main swim area. Mix canoes and paddleboards so everyone in the group gets what they want."],
         best="Hot summer days, swim-and-paddle groups, mixed canoe + SUP outings",
         tips=["Mid-afternoon is the classic Brohm window, when the water is warmest and swimming is best.",
               "Book a canoe plus a few paddleboards for a group. We deliver them together.",
               "Bring water shoes. The lake edges are rocky in places."],
         faqs=[("Do you deliver canoes to Brohm Lake?", "Yes. We drop canoes (and paddleboards) at the Brohm Lake launch and pick them up when you're done. Delivery is priced by location, so call for a quote."),
               ("Is Brohm Lake good for swimming and paddling?", "It's one of the warmest lakes near Squamish in summer, which makes it a great swim-and-paddle day."),
               ("Can we rent canoes and paddleboards together?", "Yes. Mixed groups are common at Brohm. Tell us the mix when you book.")],
         reviews=["caroline"], related=["cat-lake-canoe-rental", "alice-lake-canoe-rental", "browning-lake-canoe-rental"]),
    dict(slug="cat-lake-canoe-rental", name="Cat Lake", area="Squamish", level="Beginner",
         lat=49.8444, lon=-123.1381, img="sup-reflection.jpg",
         title="Cat Lake Canoe Rental Squamish | The Easiest Paddle in Town",
         desc="Canoe rental delivered to Cat Lake near Squamish. Small, calm and motor-free, perfect for first-timers, kids and dogs. Up to 3 paddlers, all gear included.",
         hook="Small, calm and motor-free. Cat Lake is the easiest canoe day in Squamish, and the one we recommend to anyone who has never paddled.",
         intro=["Cat Lake is a small forest lake at a recreation site just north of Brohm Lake. There are no motorboats, no current and no tide, just a quiet loop of water you can paddle around in under an hour.",
                "That's exactly why we send first-timers here. It's the place to learn how a canoe turns and to give the kids a paddle. It's also a good warm-up before trying something bigger, like the Squamish River."],
         best="First-time paddlers, young kids, dogs, short relaxed outings",
         tips=["Use it as a warm-up lake before the Echo Lake river crossing or a Howe Sound trip.",
               "Weekday mornings are quietest. The recreation site gets busy on summer weekends.",
               "It's small enough to circle in an hour, so add a picnic and a swim."],
         faqs=[("Is Cat Lake good for beginners?", "It's the easiest canoe outing in Squamish: small, calm and motor-free, with no tide or current. It's ideal for first-timers and kids."),
               ("Do you deliver to Cat Lake?", "Yes. We bring the canoe, paddles and PFDs to the launch and pick up afterward."),
               ("How long does it take to paddle around Cat Lake?", "It's a small lake, so a relaxed lap takes under an hour. Most people stay longer to swim and explore.")],
         reviews=[], related=["brohm-lake-canoe-rental", "alice-lake-canoe-rental", "echo-lake-canoe-rental"]),
    dict(slug="browning-lake-canoe-rental", name="Browning Lake (Murrin Park)", short="Browning Lake", area="Squamish", level="Beginner",
         lat=49.6475, lon=-123.2072, img="canoe-mountain.jpg",
         title="Browning Lake Canoe Rental | Murrin Provincial Park, Squamish",
         desc="Canoe rental delivered to Browning Lake in Murrin Provincial Park, just south of Squamish. A small, quiet lake under granite cliffs. Up to 3 paddlers, gear included.",
         hook="A small lake under granite cliffs in Murrin Provincial Park. It's compact, quiet and beautiful in evening light.",
         intro=["Browning Lake is the centrepiece of Murrin Provincial Park, right beside the Sea to Sky Highway just south of Squamish. Climbers know the park for its crags. Paddlers know it for a pocket of calm water surrounded by rock walls and forest.",
                "It's a short paddle rather than a big day out, which makes it a perfect after-work or evening outing, or a calm stop on the drive up from Vancouver."],
         best="Evening paddles, short outings, couples, photographers",
         tips=["Go in the evening, when the cliffs light up.",
               "Parking is limited on busy days, and delivery saves you hauling a boat from the lot.",
               "Combine it with a short walk on the park trails."],
         faqs=[("Can you deliver a canoe to Browning Lake?", "Yes. We deliver to Browning Lake in Murrin Park and pick up when you're finished."),
               ("How big is Browning Lake?", "It's small. Think an hour or two on the water, not a full day. That's part of its charm."),
               ("Is it good for beginners?", "Yes. It's sheltered flatwater with no current or tide.")],
         reviews=[], related=["alice-lake-canoe-rental", "howe-sound-canoe-rental", "squamish-estuary-canoe-rental"]),
    dict(slug="squamish-river-canoe-rental", name="Squamish River", area="Squamish", level="Intermediate",
         lat=49.7300, lon=-123.1700, img="river-canyon.jpg",
         title="Squamish River Canoe Rental | Downriver Trips & Shuttles",
         desc="Canoe rental for the Squamish River. Downriver day trips with delivery upstream and pickup downstream. Real moving water for paddlers with some experience. Gear included.",
         hook="Real moving water through the valley under the Tantalus Range. We drop you upstream and pick you up downstream.",
         intro=["The Squamish River is the big paddle in town: glacier-fed, moving and wide, running down the valley past the Tantalus Range toward the estuary and Howe Sound. A downriver canoe trip here feels like a proper expedition, even as a day trip.",
                "We handle the logistics. You pick a put-in, we deliver the canoe there, and we arrange a pickup downstream so nobody has to paddle back against the current. Jeremy will talk through the river level and the route for your date before you go."],
         best="Paddlers with moving-water experience, adventurous day trips",
         tips=["The river is high and pushy with snowmelt in late spring and early summer and calmer by late summer. Ask about levels before you book.",
               "Not a beginner paddle. Warm up on a lake first if you've never canoed in current.",
               "Watch for seals near the lower river and eagles in winter."],
         faqs=[("Can I canoe the Squamish River without experience?", "We don't recommend it. The Squamish River has real current and big seasonal swings. At least one prior moving-water trip is a good idea. Beginners should start on Cat Lake or Alice Lake."),
               ("Do you shuttle canoes for downriver trips?", "Yes. We deliver to your put-in and pick up at your take-out, so it's a one-way paddle."),
               ("Can I paddle across to Echo Lake?", "Yes. That's a separate, popular trip. See our <a href=\"/echo-lake-canoe-rental/\">Echo Lake canoe rental</a> page.")],
         reviews=["james", "axel", "peter", "zoe"], related=["echo-lake-canoe-rental", "squamish-estuary-canoe-rental", "mamquam-blind-channel-canoe-rental"]),
    dict(slug="squamish-estuary-canoe-rental", name="Squamish Estuary", area="Squamish", level="Beginner-Intermediate",
         lat=49.6900, lon=-123.1650, img="estuary-drone.jpg",
         title="Squamish Estuary Canoe Rental | Tidal Flatwater Under the Chief",
         desc="Canoe rental for the Squamish Estuary. Tidal flatwater paddling with the Stawamus Chief overhead. We help you time the tide for an easy launch. Gear included.",
         hook="Tidal flatwater with the Stawamus Chief overhead. We help you time the tide so the launch is easy and the paddle is calm.",
         intro=["The Squamish Estuary is where the river meets Howe Sound: a wide, flat maze of channels, marsh and mudflats, with the Chief and Mount Garibaldi on the skyline. It's one of the most photographed views in Squamish, and it's best seen from the water.",
                "The tide decides everything here. Go near high tide and the channels are full and easy. Go at low tide and you might be dragging the canoe across mud. We help you time your launch so you get the good version."],
         best="Sunrise paddles, photographers, birders, relaxed flatwater",
         tips=["Time your trip around high tide. We'll help you pick the window.",
               "Sunrise is the photo moment, and the wind is usually lowest early.",
               "Watch for eagles, herons and seals, and give wildlife plenty of space."],
         faqs=[("Do I need to check the tides to paddle the Squamish Estuary?", "Yes. The estuary is tidal, and low tide can leave channels too shallow to paddle. We'll help you time the launch when you book."),
               ("Is the estuary good for beginners?", "In calm conditions near high tide, yes. Afternoon wind off Howe Sound can make it harder, so mornings are best."),
               ("What wildlife will we see?", "Bald eagles, herons, waterfowl and seals are common. The estuary is an important wildlife area, so keep your distance.")],
         reviews=[], related=["mamquam-blind-channel-canoe-rental", "squamish-river-canoe-rental", "howe-sound-canoe-rental"]),
    dict(slug="mamquam-blind-channel-canoe-rental", name="Mamquam Blind Channel", area="Squamish", level="Beginner",
         lat=49.6980, lon=-123.1480, img="canoe-sunset.jpg",
         title="Mamquam Blind Channel Canoe Rental | Downtown Squamish Paddle",
         desc="Canoe rental for the Mamquam Blind Channel in downtown Squamish. A calm tidal channel steps from coffee shops. Short, relaxed paddles, delivered to the launch.",
         hook="A calm tidal channel right behind downtown Squamish. Grab a coffee, then paddle.",
         intro=["The Mamquam Blind Channel runs along the edge of downtown Squamish, a sheltered arm of water between the town and the estuary. It's the most convenient paddle in town, with no driving up the highway, and you're on the water in minutes.",
                "It's a relaxed, short outing that works when you only have a couple of hours, and it connects to the wider estuary for anyone who wants to keep going."],
         best="Short outings, visitors staying downtown, relaxed paddles",
         tips=["Like the estuary, the channel is tidal. Higher tides make for easier paddling.",
               "It's a good way to finish a downtown afternoon. Paddle first, then dinner.",
               "Confident paddlers can continue out toward the estuary."],
         faqs=[("Where is the Mamquam Blind Channel?", "It runs along the edge of downtown Squamish, between town and the Squamish Estuary."),
               ("Is it tidal?", "Yes. It's connected to Howe Sound, so the water level changes with the tide. We'll help you pick a good time."),
               ("How long is a typical paddle?", "Most people spend one to two hours. It's a short, easy outing.")],
         reviews=[], related=["squamish-estuary-canoe-rental", "squamish-river-canoe-rental", "browning-lake-canoe-rental"]),
    dict(slug="howe-sound-canoe-rental", name="Howe Sound", area="Squamish", level="Intermediate",
         lat=49.5666, lon=-123.2422, img="mountain-peak.jpg",
         title="Howe Sound Canoe Rental | Britannia, Porteau Cove & Furry Creek",
         desc="Canoe rental for Howe Sound, delivered to Britannia Beach, Porteau Cove or Furry Creek. Saltwater paddling with seals, eagles and Anvil Island views. Gear included.",
         hook="Saltwater paddling in a fjord, with seals, eagles and Anvil Island on the horizon. Best in calm morning windows.",
         intro=["Howe Sound is North America's southernmost fjord: deep saltwater framed by granite walls and mountains rising straight from the shore. Paddling here is a different world from the lakes, with seals popping up beside the boat, eagles overhead and huge views in every direction.",
                "We deliver to the Howe Sound launches along the Sea to Sky Highway, including Britannia Beach, Porteau Cove and Furry Creek, for half-day, full-day and overnight trips."],
         best="Experienced paddlers, wildlife lovers, overnight trips",
         tips=["Go early. Howe Sound's afternoon winds can build quickly and make the return hard work.",
               "Stay close to shore and keep an eye on the weather.",
               "Want to see more of the Sound without paddling? Our sister company <a href=\"https://squamishwatertaxi.com/destinations.html\">Squamish Water Taxi</a> runs boat trips to the islands."],
         faqs=[("Where do you deliver canoes on Howe Sound?", "Britannia Beach, Porteau Cove and Furry Creek are our main Howe Sound launches. Ask about others."),
               ("Is Howe Sound safe for canoeing?", "In calm conditions with some paddling experience, yes. Wind and waves can build in the afternoon, so go early and stay near shore."),
               ("Can I do an overnight Howe Sound trip?", "Yes. Multi-day rentals are available, and the canoe stays with you for the trip.")],
         reviews=["ocelab"], related=["squamish-estuary-canoe-rental", "browning-lake-canoe-rental", "squamish-river-canoe-rental"]),
    # Whistler / Pemberton
    dict(slug="alta-lake-canoe-rental", name="Alta Lake", area="Whistler", level="Beginner",
         lat=50.1150, lon=-122.9800, img="whistler.jpg",
         title="Alta Lake Canoe Rental Whistler | Rainbow, Lakeside & Wayside",
         desc="Canoe rental delivered to Alta Lake in Whistler: Rainbow Park, Lakeside Park or Wayside Park. The classic Whistler paddle. Up to 3 paddlers, gear included.",
         hook="The classic Whistler paddle, with three put-ins, warm water and mountain views. We deliver to Rainbow, Lakeside or Wayside Park.",
         intro=["Alta Lake is the main lake in the Whistler valley and the warmest of the bunch. Three parks line its shore: Rainbow Park on the west side, and Lakeside and Wayside on the east. Each has its own launch, so you can pick whichever suits your day.",
                "It's also the start of the River of Golden Dreams. Rainbow Park is the drop-off for that one-way paddle down to Green Lake."],
         best="Families, first-timers, morning paddles, River of Golden Dreams starts",
         tips=["Mornings are usually glass-calm, and afternoon thermals can pick up.",
               "Rainbow Park has the best views across to the mountains.",
               "Add the River of Golden Dreams for a one-way downstream finish."],
         faqs=[("Where on Alta Lake do you deliver?", "Rainbow Park, Lakeside Park or Wayside Park. Pick the one that suits you."),
               ("Is Alta Lake good for beginners?", "Yes, especially in the calm morning hours."),
               ("Can I paddle from Alta Lake to Green Lake?", "Yes, by the River of Golden Dreams. See our <a href=\"/river-of-golden-dreams-canoe-rental/\">River of Golden Dreams canoe shuttle</a>.")],
         reviews=[], related=["river-of-golden-dreams-canoe-rental", "lost-lake-canoe-rental", "nita-lake-canoe-rental"]),
    dict(slug="river-of-golden-dreams-canoe-rental", name="River of Golden Dreams", area="Whistler", level="Beginner-Intermediate",
         lat=50.1290, lon=-122.9620, img="river-tour.jpg",
         title="River of Golden Dreams Canoe Rental | Whistler Shuttle Service",
         desc="River of Golden Dreams canoe rental with shuttle. We drop at Rainbow Park on Alta Lake and pick up at Meadow Park on Green Lake. A 2-3 hour one-way paddle in Whistler.",
         hook="Whistler's best half-day paddle. We drop you at Rainbow Park, you float down to Green Lake, and we pick you up at Meadow Park.",
         intro=["The River of Golden Dreams winds from Alta Lake through wetlands and forest to Green Lake. It's narrow and twisty, mostly gentle, and one of the most memorable paddles in BC. The full trip takes about 2-3 hours.",
                "It's one-way, so the shuttle is what makes it easy. We drop the canoe at Rainbow Park on Alta Lake and pick it up at Meadow Park on Green Lake. No car shuffle, no paddling back upstream."],
         best="Adventurous families, couples, a classic Whistler half-day",
         tips=["Late June through July usually has the best flow.",
               "Expect tight bends, overhanging branches and the odd shallow spot. Steering matters more than speed.",
               "Read our <a href=\"/blog/river-of-golden-dreams-whistler/\">River of Golden Dreams guide</a> before you go."],
         faqs=[("How long is the River of Golden Dreams paddle?", "About 2-3 hours from Rainbow Park on Alta Lake to Meadow Park on Green Lake, depending on water levels and how often you stop."),
               ("Do you shuttle the canoe?", "Yes. We drop at Rainbow Park and pick up at Meadow Park, so it's a one-way trip."),
               ("Is it suitable for beginners?", "Confident beginners do it every summer, but you'll need to steer through tight bends. Book a calm lake first if you've never paddled.")],
         reviews=[], related=["alta-lake-canoe-rental", "green-lake-canoe-rental", "lost-lake-canoe-rental"]),
    dict(slug="green-lake-canoe-rental", name="Green Lake", area="Whistler", level="Intermediate",
         lat=50.1450, lon=-122.9400, img="glacier.jpg",
         title="Green Lake Canoe Rental Whistler | Turquoise Glacial Water",
         desc="Canoe rental delivered to Green Lake, Whistler. Turquoise glacial water under Wedge Mountain. Bigger and colder than Alta, best for confident paddlers. Gear included.",
         hook="Turquoise glacial water under Wedge Mountain. Bigger, colder and more exposed than Whistler's other lakes, and that's the appeal.",
         intro=["Green Lake sits at the north end of the Whistler valley, and its glacial colour is the reason people come. Wedge Mountain and the Armchair tower above it, and on a still morning the reflections are unreal.",
                "It's bigger and more open to the wind than Alta or Lost Lake, which is why we recommend canoes over paddleboards here and suggest some prior experience. It's also the finish line for the River of Golden Dreams."],
         best="Confident paddlers, photographers, River of Golden Dreams finishers",
         tips=["Go early for calm water and the best colour.",
               "The water is cold, so wear your PFD and stay near shore if the wind builds.",
               "Meadow Park is the take-out for the River of Golden Dreams."],
         faqs=[("Is Green Lake good for beginners?", "We recommend some prior canoe experience. It's larger and more exposed to wind than Whistler's other lakes."),
               ("Why is Green Lake so green?", "Glacial silt (rock flour) suspended in the water scatters light, which gives it that turquoise colour."),
               ("Canoe or paddleboard on Green Lake?", "Canoe. It handles the wind and chop much better than a SUP when conditions change.")],
         reviews=[], related=["river-of-golden-dreams-canoe-rental", "alta-lake-canoe-rental", "one-mile-lake-canoe-rental"]),
    dict(slug="lost-lake-canoe-rental", name="Lost Lake", area="Whistler", level="Beginner",
         lat=50.1290, lon=-122.9430, img="forest-canopy.jpg",
         title="Lost Lake Canoe Rental Whistler | Walking Distance from the Village",
         desc="Canoe rental at Lost Lake, walking distance from Whistler Village. No motorboats, easy swim breaks, great for families with young kids. Up to 3 paddlers, gear included.",
         hook="Walking distance from Whistler Village, with no motorboats and plenty of swim breaks. The easy family pick.",
         intro=["Lost Lake is the closest lake to Whistler Village. It's tucked into the forest at the end of a short walk or ride, with a beach, a dock and trails all the way around. There are no motorboats, so the water stays calm and quiet.",
                "It's a small lake, perfect for families with young kids in the canoe, a first paddle, or a quick outing between other Whistler plans."],
         best="Families with young kids, first-timers, visitors staying in the village",
         tips=["Head past the main beach for quieter water.",
               "It's a good warm-up before trying the River of Golden Dreams.",
               "Pair it with the Lost Lake trails for a full afternoon."],
         faqs=[("Can I walk to Lost Lake from Whistler Village?", "Yes. It's walking distance from the village and the Upper Village."),
               ("Is Lost Lake good for kids?", "Very. It's small, calm and motor-free, with easy swim breaks."),
               ("Do you deliver to Lost Lake?", "Yes. Tell us your time and we'll meet you with the canoe and gear.")],
         reviews=[], related=["alta-lake-canoe-rental", "alpha-lake-canoe-rental", "nita-lake-canoe-rental"]),
    dict(slug="nita-lake-canoe-rental", name="Nita Lake", area="Whistler", level="Beginner",
         lat=50.0960, lon=-123.0020, img="canoe-sunset.jpg",
         title="Nita Lake Canoe Rental Whistler | Quiet Sunrise & Sunset Paddles",
         desc="Canoe rental delivered to Nita Lake in Whistler Creekside. Small, quiet and almost always glass-calm. Prime sunrise and sunset paddling. Up to 3 paddlers, gear included.",
         hook="Small, quiet and almost always glass-calm. Nita Lake is Whistler's sunrise and sunset paddle.",
         intro=["Nita Lake sits just behind Whistler Creekside, small and sheltered, with less traffic than Alta or Lost Lake. On a calm evening the surface turns to glass and reflects the mountains.",
                "It's not a big paddle. It's a beautiful one, and the one we suggest to couples and anyone who wants a quiet hour on the water."],
         best="Couples, sunrise and sunset paddles, quiet outings",
         tips=["Time it for golden hour.",
               "Easy parking and fewer crowds than the bigger lakes.",
               "Pair it with dinner in Creekside."],
         faqs=[("Where is Nita Lake?", "Just behind Whistler Creekside, at the south end of the valley."),
               ("Is it busy?", "Usually quieter than Alta or Lost Lake, which is a big part of its appeal."),
               ("Is it good for beginners?", "Yes. It's small and sheltered, and usually calm.")],
         reviews=[], related=["alpha-lake-canoe-rental", "alta-lake-canoe-rental", "lost-lake-canoe-rental"]),
    dict(slug="alpha-lake-canoe-rental", name="Alpha Lake", area="Whistler", level="Beginner",
         lat=50.0880, lon=-123.0410, img="sup-lake.jpg",
         title="Alpha Lake Canoe Rental Whistler | Family-Friendly Creekside Lake",
         desc="Canoe rental delivered to Alpha Lake at the south end of Whistler. Calm, shallow water with a beach park and dock, perfect for a first family paddle. Gear included.",
         hook="A calm, shallow Creekside lake with a beach park and dock. It's the easy pick with kids.",
         intro=["Alpha Lake sits at the south end of Whistler, with a beach park, a dock and a gentle shoreline. The water is calm and forgiving, which makes it ideal for a first family canoe outing.",
                "It's smaller and more relaxed than Alta Lake, a local's lake where you can spend the afternoon switching between paddling and the beach."],
         best="Families with kids, first-time paddlers, beach afternoons",
         tips=["Shallow, warm edges make swim breaks easy.",
               "It's a good first lake before moving on to Alta or Green.",
               "Bring a picnic. The beach park makes a full afternoon easy."],
         faqs=[("Is Alpha Lake good for kids?", "Yes. It's calm and shallow, with a beach park, which makes it the easy family pick."),
               ("Where is Alpha Lake?", "At the south end of Whistler, near Creekside."),
               ("Do you deliver to Alpha Lake?", "Yes. We meet you at the launch with the canoe, paddles and PFDs.")],
         reviews=[], related=["nita-lake-canoe-rental", "lost-lake-canoe-rental", "alta-lake-canoe-rental"]),
    dict(slug="one-mile-lake-canoe-rental", name="One Mile Lake", area="Pemberton", level="Beginner",
         lat=50.3150, lon=-122.8100, img="camping.jpg",
         title="One Mile Lake Canoe Rental | Pemberton Paddling, Delivered",
         desc="Canoe rental delivered to One Mile Lake in Pemberton, 25 minutes north of Whistler. Warmer, quieter water with a family beach park and easy launch. Gear included.",
         hook="Warmer, quieter water 25 minutes north of Whistler, with a family beach park and an easy launch.",
         intro=["One Mile Lake sits at the edge of Pemberton, a small lake with a beach park, an easy launch and Mount Currie on the skyline. It's usually warmer and far less busy than the Whistler lakes in peak season.",
                "It's a great escape when Whistler is packed, or an easy add-on if you're staying in Pemberton."],
         best="Families, crowd-free summer days, Pemberton visitors",
         tips=["Go when the Whistler lakes are busy. One Mile is usually much quieter.",
               "The beach park makes it easy to mix paddling with swimming.",
               "Ask about pairing it with a Whistler delivery on a multi-day rental."],
         faqs=[("How far is One Mile Lake from Whistler?", "About 25 minutes north, on the edge of Pemberton."),
               ("Is One Mile Lake good for beginners?", "Yes. It's small, calm and has an easy launch."),
               ("Do you deliver to Pemberton?", "Yes. One Mile Lake is one of our regular delivery spots. Delivery is priced by location.")],
         reviews=[], related=["green-lake-canoe-rental", "alpha-lake-canoe-rental", "lost-lake-canoe-rental"]),
]

# Existing hand-built page, included in hub + related.
EXTRA = {"echo-lake-canoe-rental": dict(name="Echo Lake (River Crossing)", short="Echo Lake", area="Squamish", level="Intermediate",
                                        hook="Paddle across the Squamish River to the Echo Falls trailhead.")}
BY_SLUG = {p["slug"]: p for p in PLACES}
BY_SLUG.update(EXTRA)
AREA_HUB = {"Squamish": "/canoe-delivery-squamish/", "Whistler": "/canoe-delivery-whistler/", "Pemberton": "/canoe-delivery-whistler/"}


def e(s):
    return html.escape(s, quote=True)


def plain(s):
    return re.sub(r"<[^>]+>", "", html.unescape(s))


def head(title, desc, url, img, ld, lat=None, lon=None):
    geo = f'  <meta name="geo.region" content="CA-BC">\n  <meta name="geo.position" content="{lat};{lon}">\n  <meta name="ICBM" content="{lat}, {lon}">\n' if lat else ""
    lds = "\n".join(f'  <script type="application/ld+json">\n{json.dumps(x, indent=2, ensure_ascii=False)}\n  </script>' for x in ld)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{e(title)}</title>
  <link rel="icon" type="image/svg+xml" href="/favicon.svg">
  <meta name="description" content="{e(desc)}">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="{url}">
  <meta property="og:title" content="{e(title)}">
  <meta property="og:description" content="{e(desc)}">
  <meta property="og:type" content="website">
  <meta property="og:url" content="{url}">
  <meta property="og:image" content="{SITE}/images/{img}">
  <meta property="og:locale" content="en_CA">
  <meta property="og:site_name" content="Squamish &amp; Whistler Canoe Rental">
  <meta name="twitter:card" content="summary_large_image">
{geo}
{lds}

  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700;800&family=Barlow:wght@300;400;500;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="../style.css">
  <style>
    .crumbs {{ font-size:.9rem; margin:0 0 1rem; opacity:.75; }}
    .related-grid {{ display:grid; gap:1rem; grid-template-columns:repeat(auto-fit,minmax(230px,1fr)); margin-top:2rem; }}
    .related-grid a {{ display:block; padding:1.25rem; border:1px solid rgba(0,0,0,.12); border-radius:10px; text-decoration:none; color:inherit; background:#fff; }}
    .related-grid a strong {{ display:block; margin-bottom:.35rem; }}
    .related-grid a span {{ font-size:.85rem; opacity:.7; }}
    .related-grid a:hover {{ border-color:currentColor; }}
  </style>
</head>
<body>

{NAV}"""


def provider():
    return {"@type": "LocalBusiness", "@id": f"{SITE}/#business", "name": "Squamish & Whistler Canoe Rental",
            "telephone": "+16048498898", "email": "squamishcanoerental@gmail.com", "url": SITE,
            "address": {"@type": "PostalAddress", "addressLocality": "Squamish", "addressRegion": "BC", "addressCountry": "CA"}}


def card(slug):
    p = BY_SLUG[slug]
    return f'        <a href="/{slug}/"><strong>{e(p.get("short", p["name"]))}</strong>{e(plain(p["hook"]))}<br><span>{p["area"]} &middot; {p["level"]}</span></a>'


def page(p):
    url = f"{SITE}/{p['slug']}/"
    short = p.get("short", p["name"])
    ld = [
        {"@context": "https://schema.org", "@type": "Service", "serviceType": "Canoe Rental",
         "name": f"{short} Canoe Rental", "description": p["desc"], "url": url,
         "areaServed": {"@type": "Place", "name": p["name"],
                        "geo": {"@type": "GeoCoordinates", "latitude": p["lat"], "longitude": p["lon"]},
                        "containedInPlace": {"@type": "City", "name": p["area"]}},
         "provider": provider(),
         "offers": {"@type": "Offer", "availability": "https://schema.org/InStock", "url": BOOK}},
        {"@context": "https://schema.org", "@type": "FAQPage",
         "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": plain(a)}} for q, a in p["faqs"]]},
        {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": "Where to Paddle", "item": SITE + "/canoe-rental-locations/"},
            {"@type": "ListItem", "position": 3, "name": short, "item": url}]},
    ]
    out = [head(p["title"], p["desc"], url, p["img"], ld, p["lat"], p["lon"])]
    out.append(f"""  <header class="hero" id="hero">
    <div class="hero-bg">
      <img src="../images/{p['img']}" alt="Canoe on {e(p['name'])}, {p['area']}, BC" loading="eager">
      <div class="hero-overlay"></div>
    </div>
    <div class="hero-content">
      <p class="hero-label">{p['area']}, BC &middot; {e(p['name'])}</p>
      <h1>{e(short)} Canoe Rental</h1>
      <p class="hero-tagline">{p['hook']} Up to 3 paddlers per canoe.</p>
      <div class="hero-actions">
        <a href="{BOOK}" target="_blank" rel="noopener" class="btn btn-primary">Book a Canoe</a>
        <a href="tel:6048498898" class="btn btn-outline">Call (604) 849-8898</a>
      </div>
    </div>
  </header>

  <section class="section about">
    <div class="container">
      <p class="crumbs"><a href="/">Home</a> &rsaquo; <a href="/canoe-rental-locations/">Where to Paddle</a> &rsaquo; {e(short)}</p>
      <div class="about-text" style="max-width:800px;">
        <p class="section-label">Paddling {e(short)}</p>
        <h2>{e(short)}, delivered.</h2>
        {''.join(f'<p>{x}</p>' for x in p['intro'])}
        <div class="about-stats">
          <div class="stat"><span class="stat-number">{p['level']}</span><span class="stat-label">Skill Level</span></div>
          <div class="stat"><span class="stat-number">Up to 3</span><span class="stat-label">Paddlers Per Canoe</span></div>
          <div class="stat"><span class="stat-number">Delivered</span><span class="stat-label">Priced by Location</span></div>
        </div>
        <p><strong>Best for:</strong> {e(p['best'])}.</p>
      </div>
    </div>
  </section>

  <section class="section services">
    <div class="container">
      <p class="section-label center">Local Knowledge</p>
      <h2 class="section-title">Tips for {e(short)}</h2>
      <div class="services-grid">
{chr(10).join(f'        <div class="service-card"><p>{t}</p></div>' for t in p['tips'])}
      </div>
      <div class="amenities">
        <h3>Every Rental Includes</h3>
        <div class="amenities-list">
          <div class="amenity">&#10003; Canoe (seats up to 3)</div>
          <div class="amenity">&#10003; Paddles</div>
          <div class="amenity">&#10003; PFDs / Life Jackets</div>
          <div class="amenity">&#10003; Bailer &amp; Safety Whistle</div>
          <div class="amenity">&#10003; Delivery &amp; Pickup</div>
          <div class="amenity">&#10003; Local Routing Advice</div>
        </div>
      </div>
    </div>
  </section>
""")
    if p["reviews"]:
        cards = "\n".join(f"""        <div class="testimonial-card">
          <div class="stars">&#9733;&#9733;&#9733;&#9733;&#9733;</div>
          <blockquote>"{REVIEWS[r][1]}"</blockquote>
          <div class="testimonial-author"><span class="review-source">Google Review</span><strong>{REVIEWS[r][0]}</strong></div>
        </div>""" for r in p["reviews"])
        out.append(f"""  <section class="section testimonials">
    <div class="container">
      <p class="section-label center">5-Star Google Reviews</p>
      <h2 class="section-title">Paddlers on {e(short)}</h2>
    </div>
    <div class="reviews-scroll-wrap">
      <div class="reviews-scroll">
{cards}
      </div>
    </div>
  </section>
""")
    faqs = "\n".join(f"        <h3>{e(q)}</h3>\n        <p>{a}</p>" for q, a in p["faqs"])
    out.append(f"""  <section class="section about">
    <div class="container">
      <p class="section-label center">Good to Know</p>
      <h2 class="section-title">{e(short)} Canoe Rental FAQ</h2>
      <div class="about-text" style="max-width:800px;margin:2rem auto 0;">
{faqs}
        <h3>More {p['area']} paddling</h3>
        <p>See all our <a href="{AREA_HUB[p['area']]}">{'Whistler &amp; Pemberton' if p['area'] != 'Squamish' else 'Squamish'} canoe delivery</a> spots, or browse <a href="/canoe-rental-locations/">every place we deliver</a>.</p>
      </div>
      <div class="related-grid">
{chr(10).join(card(s) for s in p['related'])}
      </div>
    </div>
  </section>

  <section class="section booking" id="book">
    <div class="container">
      <div class="booking-content">
        <p class="section-label center">Ready?</p>
        <h2 class="section-title">Book Your {e(short)} Canoe</h2>
        <p class="booking-text">Pick your date, tell us it's {e(short)}, and we'll have the canoe waiting at the launch.</p>
        <div class="booking-actions">
          <a href="{BOOK}" target="_blank" rel="noopener" class="btn btn-primary btn-lg">Book Online</a>
          <a href="tel:6048498898" class="btn btn-outline btn-lg">Call (604) 849-8898</a>
        </div>
        <p class="booking-note">Or email <a href="mailto:squamishcanoerental@gmail.com">squamishcanoerental@gmail.com</a></p>
      </div>
    </div>
  </section>

{FOOTER}</body>
</html>
""")
    return "".join(out)


def hub():
    url = f"{SITE}/canoe-rental-locations/"
    title = "Where to Canoe in Squamish & Whistler | 16 Lakes & Rivers"
    desc = "Every lake, river and shoreline we deliver canoes to in Squamish, Whistler and Pemberton, with skill levels, tips and booking. Alice, Brohm, Alta, Green, Howe Sound and more."
    order = [s for s in BY_SLUG]
    ld = [{"@context": "https://schema.org", "@type": "ItemList", "name": "Canoe rental locations",
           "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": f"{SITE}/{s}/", "name": BY_SLUG[s].get("short", BY_SLUG[s]["name"])} for i, s in enumerate(order)]}]
    out = [head(title, desc, url, "canoe-mountain.jpg", ld)]
    sections = []
    for area, label in [("Squamish", "Squamish"), ("Whistler", "Whistler"), ("Pemberton", "Pemberton")]:
        slugs = [s for s in order if BY_SLUG[s]["area"] == area]
        sections.append(f"""      <h2 class="section-title" style="margin-top:3rem;">{label}</h2>
      <div class="related-grid">
{chr(10).join(card(s) for s in slugs)}
      </div>""")
    out.append(f"""  <header class="hero" id="hero">
    <div class="hero-bg">
      <img src="../images/canoe-mountain.jpg" alt="Canoe on a calm lake below the mountains near Squamish" loading="eager">
      <div class="hero-overlay"></div>
    </div>
    <div class="hero-content">
      <p class="hero-label">Squamish &middot; Whistler &middot; Pemberton</p>
      <h1>Where to Paddle</h1>
      <p class="hero-tagline">Every lake, river and shoreline we deliver canoes to, with honest skill levels and local tips for each.</p>
      <div class="hero-actions">
        <a href="{BOOK}" target="_blank" rel="noopener" class="btn btn-primary">Book a Canoe</a>
        <a href="tel:6048498898" class="btn btn-outline">Call (604) 849-8898</a>
      </div>
    </div>
  </header>

  <section class="section about">
    <div class="container">
      <p class="crumbs"><a href="/">Home</a> &rsaquo; Where to Paddle</p>
      <div class="about-text" style="max-width:800px;">
        <p>New to paddling? Start with a <strong>Beginner</strong> lake like Cat Lake, Alice Lake or Lost Lake. Spots marked <strong>Intermediate</strong> have current, wind or open water, so build up to those. Not sure which is right? Call <a href="tel:6048498898">(604) 849-8898</a> and Jeremy will match a spot to your group.</p>
      </div>
{chr(10).join(sections)}
    </div>
  </section>

{FOOTER}</body>
</html>
""")
    return "".join(out)


def main():
    for p in PLACES:
        d = ROOT / p["slug"]
        d.mkdir(exist_ok=True)
        (d / "index.html").write_text(page(p))
    (ROOT / "canoe-rental-locations").mkdir(exist_ok=True)
    (ROOT / "canoe-rental-locations/index.html").write_text(hub())
    sm = (ROOT / "sitemap.xml").read_text()
    add = ["canoe-rental-locations/"] + [p["slug"] + "/" for p in PLACES]
    new = "".join(f"  <url>\n    <loc>{SITE}/{s}</loc>\n    <changefreq>monthly</changefreq>\n    <priority>0.7</priority>\n  </url>\n"
                  for s in add if f"<loc>{SITE}/{s}</loc>" not in sm)
    if new:
        (ROOT / "sitemap.xml").write_text(sm.replace("</urlset>", new + "</urlset>"))
    print(f"built {len(PLACES)} location pages + hub")


if __name__ == "__main__":
    main()
