from __future__ import annotations

from django_spire.knowledge.entry.version.block.data.heading_data import HeadingEditorBlockData
from django_spire.knowledge.entry.version.block.data.text_data import TextEditorBlockData


LADDER_SAFETY_BLOCKS = [
    HeadingEditorBlockData(text='Ladder Safety: A Journey Through the Heights',
                           level=1),
    TextEditorBlockData(text=''),
    HeadingEditorBlockData(text='The Great Ladder Adventure Begins', level=2),
    TextEditorBlockData(
        text='Welcome to the thrilling world of ladder safety! Grab your hard hats and let\'s explore the wonderful dangers of working at heights.'),
    TextEditorBlockData(
        text='Whether you\'re a seasoned climber or a first-time ladder user, this guide will help you navigate the exciting landscape of aerial safety.'),
    TextEditorBlockData(text=''),
    HeadingEditorBlockData(text='High vs. Low: The Ladder Tightrope', level=2),
    TextEditorBlockData(
        text='High ladders are like climbing Mount Everest - exciting but dangerous! Always double-check your footing and support.'),
    TextEditorBlockData(
        text='Low ladders might seem harmless, but they\'re like slippery snakes waiting to trip you up! Keep them out of high-traffic areas.'),
    TextEditorBlockData(text=''),
    HeadingEditorBlockData(text='The Ladder Safety Toolkit', level=2),
    TextEditorBlockData(
        text='Inspect your ladder like a detective looking for clues - check for cracks, rust, or missing rungs.'),
    TextEditorBlockData(
        text='Remember: Three points of contact keeps you safe and sound!'),
    TextEditorBlockData(
        text='Never exceed the weight limit - your ladder has a maximum capacity just like you have a maximum capacity for pizza!'),
    TextEditorBlockData(text=''),
    HeadingEditorBlockData(text='Emergency: The Ladder Rescue Mission', level=2),
    TextEditorBlockData(
        text='If you find yourself in a precarious situation, stay calm and follow the emergency protocols.'),
    TextEditorBlockData(
        text='First aid training is like having a superhero power - it\'s invaluable when you need it most!'),
    TextEditorBlockData(text=''),
    HeadingEditorBlockData(text='The Ladder Safety Certificate', level=2),
    TextEditorBlockData(
        text='Congratulations! You\'ve completed your ladder safety course. Now go out there and climb with confidence!'),
]

KITCHEN_SAFETY_BLOCKS = [
    TextEditorBlockData(text=''),
    HeadingEditorBlockData(text='Kitchen Safety: A Culinary Adventure', level=1),
    TextEditorBlockData(text=''),
    HeadingEditorBlockData(text='The Great Kitchen Escape', level=2),
    TextEditorBlockData(
        text='Welcome to the thrilling world of kitchen safety! Every chef needs to know how to navigate the kitchen without getting burned, cut, or startled by hot oil.'),
    TextEditorBlockData(
        text='Whether you\'re a professional chef or a home cook, these safety tips will help you avoid kitchen disasters and keep your cooking adventures safe.'),
    TextEditorBlockData(text=''),
    HeadingEditorBlockData(text='Hot Oil: The Dangerous Dance', level=2),
    TextEditorBlockData(
        text='Hot oil is like a wild animal - it can splash and burn in seconds! Always use proper protective gear when handling hot oil.'),
    TextEditorBlockData(
        text='Never leave hot oil unattended, or you\'ll end up with a kitchen fire that\'s more exciting than your favorite TV show!'),
    TextEditorBlockData(text=''),
    HeadingEditorBlockData(text='Knife Safety: The Sharp Edge of Responsibility',
                           level=2),
    TextEditorBlockData(
        text='Knives are like any other tool - they\'re only as dangerous as the person using them.'),
    TextEditorBlockData(
        text='Always cut away from your body and keep your knives sharp (dull knives are actually more dangerous than sharp ones).'),
    TextEditorBlockData(text=''),
    HeadingEditorBlockData(text='Emergency Kitchen Procedures', level=2),
    TextEditorBlockData(
        text='If you encounter a kitchen emergency, stay calm and follow established protocols.'),
    TextEditorBlockData(
        text='Having a fire extinguisher in the kitchen is like having a superhero sidekick - it\'s always good to have backup!'),
]

GARDEN_SAFETY_BLOCKS = [
    TextEditorBlockData(text=''),
    HeadingEditorBlockData(text='Garden Safety: A Green Thumb Guide', level=1),
    TextEditorBlockData(text=''),
    HeadingEditorBlockData(text='The Garden Adventure Begins', level=2),
    TextEditorBlockData(
        text='Step into the wonderful world of gardening with safety as your companion! Every gardener should know how to protect themselves from thorns, chemicals, and unexpected wildlife.'),
    TextEditorBlockData(
        text='Whether you\'re tending to a small potted plant or a large garden, these tips will keep you safe while you nurture your green thumb.'),
    TextEditorBlockData(text=''),
    HeadingEditorBlockData(text='Chemical Safety: The Poisonous Garden', level=2),
    TextEditorBlockData(
        text='Gardening chemicals can be like hidden traps - they look harmless but can cause serious harm if not handled properly.'),
    TextEditorBlockData(
        text='Always read labels and wear protective gear when working with fertilizers, pesticides, or other garden chemicals.'),
    TextEditorBlockData(text=''),
    HeadingEditorBlockData(text='Tool Safety: The Gardener\'s Arsenal', level=2),
    TextEditorBlockData(
        text='Gardening tools are like weapons - they\'re only as dangerous as the person wielding them.'),
    TextEditorBlockData(
        text='Keep your tools sharp and clean to prevent accidents and ensure maximum efficiency in your garden work.'),
    TextEditorBlockData(text=''),
    HeadingEditorBlockData(text='Emergency Garden Procedures', level=2),
    TextEditorBlockData(
        text='If you encounter a garden emergency, stay calm and follow established protocols.'),
    TextEditorBlockData(
        text='Having a first aid kit in the garden is like having a superhero sidekick - it\'s always good to have backup!'),
]

OFFICE_SAFETY_BLOCKS = [
    TextEditorBlockData(text=''),
    HeadingEditorBlockData(text='Office Safety: A Professional Adventure', level=1),
    TextEditorBlockData(text=''),
    HeadingEditorBlockData(text='The Office Escape', level=2),
    TextEditorBlockData(
        text='Welcome to the exciting world of office safety! Every professional should know how to navigate their workspace without tripping, falling, or getting distracted by a rogue cable.'),
    TextEditorBlockData(
        text='Whether you\'re working in a bustling office or a quiet cubicle, these safety tips will help you avoid workplace disasters and keep your productivity high.'),
    TextEditorBlockData(text=''),
    HeadingEditorBlockData(text='Cable Safety: The Hidden Danger', level=2),
    TextEditorBlockData(
        text='Office cables are like snakes waiting to strike - they can trip you up if you\'re not careful!'),
    TextEditorBlockData(
        text='Always secure cables properly and keep walkways clear of obstacles.'),
    TextEditorBlockData(text=''),
    HeadingEditorBlockData(text='Ergonomic Safety: The Comfort Zone', level=2),
    TextEditorBlockData(
        text='Proper ergonomics in the office are like having a personal assistant - they make everything easier and more comfortable.'),
    TextEditorBlockData(
        text='Adjust your chair, monitor, and keyboard to prevent strain and injury.'),
    TextEditorBlockData(text=''),
    HeadingEditorBlockData(text='Emergency Office Procedures', level=2),
    TextEditorBlockData(
        text='If you encounter an office emergency, stay calm and follow established protocols.'),
    TextEditorBlockData(
        text='Having a fire extinguisher in the office is like having a superhero sidekick - it\'s always good to have backup!'),
]

POOL_SAFETY_BLOCKS = [
    TextEditorBlockData(text=''),
    HeadingEditorBlockData(text='Swimming Pool Safety: A Water Adventure', level=1),
    TextEditorBlockData(text=''),
    HeadingEditorBlockData(text='The Pool Party Begins', level=2),
    TextEditorBlockData(
        text='Dive into the exciting world of pool safety! Every swimmer should know how to protect themselves from drowning, sunburn, and unexpected water hazards.'),
    TextEditorBlockData(
        text='Whether you\'re swimming in a backyard pool or a public facility, these tips will keep you safe while you enjoy the water.'),
    TextEditorBlockData(text=''),
    HeadingEditorBlockData(text='Water Safety: The Deep End', level=2),
    TextEditorBlockData(
        text='Pool water can be deceiving - it looks calm but can hide dangerous situations!'),
    TextEditorBlockData(
        text='Always swim with a buddy and never dive into shallow water.'),
    TextEditorBlockData(text=''),
    HeadingEditorBlockData(text='Sun Protection: The Beach Adventure', level=2),
    TextEditorBlockData(
        text='Sun exposure is like a wild animal - it can burn you in seconds!'),
    TextEditorBlockData(
        text='Apply sunscreen regularly and wear protective clothing to avoid sunburn and skin damage.'),
    TextEditorBlockData(text=''),
    HeadingEditorBlockData(text='Emergency Pool Procedures', level=2),
    TextEditorBlockData(
        text='If you encounter a pool emergency, stay calm and follow established protocols.'),
    TextEditorBlockData(
        text='Having lifeguards on duty is like having a superhero sidekick - it\'s always good to have backup!'),
]

CONSTRUCTION_SAFETY_BLOCKS = [
    TextEditorBlockData(text=''),
    HeadingEditorBlockData(text='Construction Safety: A Building Adventure', level=1),
    TextEditorBlockData(text=''),
    HeadingEditorBlockData(text='The Construction Zone', level=2),
    TextEditorBlockData(
        text='Step into the exciting world of construction safety! Every builder should know how to protect themselves from falling objects, electrical hazards, and unexpected structural issues.'),
    TextEditorBlockData(
        text='Whether you\'re working on a skyscraper or a small home renovation, these safety tips will keep you safe while you build your dreams.'),
    TextEditorBlockData(text=''),
    HeadingEditorBlockData(text='Falling Object Safety: The Sky is Falling', level=2),
    TextEditorBlockData(
        text='Construction sites are like a battlefield - falling objects can strike at any moment!'),
    TextEditorBlockData(
        text='Always wear proper head protection and stay clear of work zones.'),
    TextEditorBlockData(text=''),
    HeadingEditorBlockData(text='Electrical Safety: The Power Adventure', level=2),
    TextEditorBlockData(
        text='Electricity is like a wild animal - it can shock you in seconds!'),
    TextEditorBlockData(
        text='Always check electrical equipment before use and never work on live circuits.'),
    TextEditorBlockData(text=''),
    HeadingEditorBlockData(text='Emergency Construction Procedures', level=2),
    TextEditorBlockData(
        text='If you encounter a construction emergency, stay calm and follow established protocols.'),
    TextEditorBlockData(
        text='Having safety officers on site is like having a superhero sidekick - it\'s always good to have backup!'),
]

CYCLING_SAFETY_BLOCKS = [
    TextEditorBlockData(text=''),
    HeadingEditorBlockData(text='Bicycle Safety: A Cycling Adventure', level=1),
    TextEditorBlockData(text=''),
    HeadingEditorBlockData(text='The Road Ahead', level=2),
    TextEditorBlockData(
        text='Ride into the exciting world of bicycle safety! Every cyclist should know how to protect themselves from traffic, weather hazards, and mechanical failures.'),
    TextEditorBlockData(
        text='Whether you\'re commuting or going for a weekend ride, these tips will keep you safe while you enjoy the open road.'),
    TextEditorBlockData(text=''),
    HeadingEditorBlockData(text='Traffic Safety: The Highway Adventure', level=2),
    TextEditorBlockData(
        text='Riding in traffic is like navigating a busy city - always stay alert and follow traffic rules!'),
    TextEditorBlockData(
        text='Always wear a helmet and make sure your bike is properly equipped with lights and reflectors.'),
    TextEditorBlockData(text=''),
    HeadingEditorBlockData(text='Weather Safety: The Elements Adventure', level=2),
    TextEditorBlockData(
        text='Weather conditions can change quickly - always check the forecast before heading out!'),
    TextEditorBlockData(
        text='Avoid riding in rain or snow without proper gear and equipment.'),
    TextEditorBlockData(text=''),
    HeadingEditorBlockData(text='Emergency Bicycle Procedures', level=2),
    TextEditorBlockData(
        text='If you encounter a bicycle emergency, stay calm and follow established protocols.'),
    TextEditorBlockData(
        text='Having a repair kit on hand is like having a superhero sidekick - it\'s always good to have backup!'),
]

FIRE_SAFETY_BLOCKS = [
    TextEditorBlockData(text=''),
    HeadingEditorBlockData(text='Fire Safety: A Blaze Adventure', level=1),
    TextEditorBlockData(text=''),
    HeadingEditorBlockData(text='The Fire Escape', level=2),
    TextEditorBlockData(
        text='Enter the exciting world of fire safety! Every person should know how to protect themselves from flames, smoke, and unexpected fires.'),
    TextEditorBlockData(
        text='Whether you\'re at home or in a public building, these tips will keep you safe while you navigate fire hazards.'),
    TextEditorBlockData(text=''),
    HeadingEditorBlockData(text='Fire Prevention: The Prevention Adventure', level=2),
    TextEditorBlockData(
        text='Prevention is better than cure - always keep fire extinguishers accessible and never leave candles unattended!'),
    TextEditorBlockData(
        text='Keep flammable materials away from heat sources and maintain proper ventilation.'),
    TextEditorBlockData(text=''),
    HeadingEditorBlockData(text='Evacuation Safety: The Escape Route', level=2),
    TextEditorBlockData(
        text='Knowing your escape routes is like having a superhero power - it\'s invaluable when you need it most!'),
    TextEditorBlockData(
        text='Always practice evacuation drills and keep emergency contact information handy.'),
    TextEditorBlockData(text=''),
    HeadingEditorBlockData(text='Emergency Fire Procedures', level=2),
    TextEditorBlockData(
        text='If you encounter a fire emergency, stay calm and follow established protocols.'),
    TextEditorBlockData(
        text='Having fire safety training is like having a superhero sidekick - it\'s always good to have backup!'),
]

HIKING_SAFETY_BLOCKS = [
    TextEditorBlockData(text=''),
    HeadingEditorBlockData(text='Hiking Safety: A Mountain Adventure', level=1),
    TextEditorBlockData(text=''),
    HeadingEditorBlockData(text='The Trail Ahead', level=2),
    TextEditorBlockData(
        text='Embark on the exciting world of hiking safety! Every hiker should know how to protect themselves from weather hazards, wildlife encounters, and unexpected terrain.'),
    TextEditorBlockData(
        text='Whether you\'re taking a short walk or a multi-day trek, these tips will keep you safe while you explore nature.'),
    TextEditorBlockData(text=''),
    HeadingEditorBlockData(text='Weather Safety: The Elements Adventure', level=2),
    TextEditorBlockData(
        text='Weather conditions can change quickly in the wilderness - always check forecasts before heading out!'),
    TextEditorBlockData(
        text='Pack appropriate gear for all weather conditions and never hike alone in dangerous areas.'),
    TextEditorBlockData(text=''),
    HeadingEditorBlockData(text='Wildlife Safety: The Animal Encounter', level=2),
    TextEditorBlockData(
        text='Wild animals are like wild cards - they can appear at any moment and behave unpredictably!'),
    TextEditorBlockData(
        text='Keep food stored properly and maintain a safe distance from wildlife.'),
    TextEditorBlockData(text=''),
    HeadingEditorBlockData(text='Emergency Hiking Procedures', level=2),
    TextEditorBlockData(
        text='If you encounter a hiking emergency, stay calm and follow established protocols.'),
    TextEditorBlockData(
        text='Having a first aid kit and emergency communication device is like having a superhero sidekick - it\'s always good to have backup!'),
]

BOATING_SAFETY_BLOCKS = [
    TextEditorBlockData(text=''),
    HeadingEditorBlockData(text='Boating Safety: A Water Adventure', level=1),
    TextEditorBlockData(text=''),
    HeadingEditorBlockData(text='The Ocean Escape', level=2),
    TextEditorBlockData(
        text='Set sail into the exciting world of boating safety! Every sailor should know how to protect themselves from water hazards, weather conditions, and unexpected emergencies.'),
    TextEditorBlockData(
        text='Whether you\'re on a small boat or a large vessel, these tips will keep you safe while you enjoy the water.'),
    TextEditorBlockData(text=''),
    HeadingEditorBlockData(text='Water Safety: The Ocean Adventure', level=2),
    TextEditorBlockData(
        text='Boating on water is like navigating a wild ocean - always stay alert and follow safety protocols!'),
    TextEditorBlockData(
        text='Always wear life jackets and check weather conditions before heading out.'),
    TextEditorBlockData(text=''),
    HeadingEditorBlockData(text='Navigation Safety: The Compass Adventure', level=2),
    TextEditorBlockData(
        text='Proper navigation is like having a superhero power - it\'s invaluable when you need it most!'),
    TextEditorBlockData(
        text='Use proper navigation equipment and never navigate without a backup plan.'),
    TextEditorBlockData(text=''),
    HeadingEditorBlockData(text='Emergency Boating Procedures', level=2),
    TextEditorBlockData(
        text='If you encounter a boating emergency, stay calm and follow established protocols.'),
    TextEditorBlockData(
        text='Having safety equipment on board is like having a superhero sidekick - it\'s always good to have backup!'),
]


SAFETY_BLOCKS = [
    LADDER_SAFETY_BLOCKS,
    KITCHEN_SAFETY_BLOCKS,
    GARDEN_SAFETY_BLOCKS,
    OFFICE_SAFETY_BLOCKS,
    POOL_SAFETY_BLOCKS,
    CONSTRUCTION_SAFETY_BLOCKS,
    CYCLING_SAFETY_BLOCKS,
    FIRE_SAFETY_BLOCKS,
    HIKING_SAFETY_BLOCKS,
    BOATING_SAFETY_BLOCKS,
]
