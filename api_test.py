
from deidentification import (
    Deidentification,
    DeidentificationConfig,
)

STORIES = [
    """John Smith was a quiet man who preferred spending his days alone. One afternoon, he found himself lost in thought, wondering if he had made the right decisions in life. His mind drifted back to the choices that had led him to where he was, and he realized he had never really given much thought to the future. Despite the uncertainty, John was content with the man he had become, trusting in himself and Michael to navigate whatever came next.""",
    """Alice and Bob decided to take a spontaneous road trip to the coast, where she hoped to photograph lighthouses while he wanted to try surfing for himself. During their journey, Bob got them completely lost when his GPS stopped working, but Alice managed to navigate them back on track using her old-fashioned paper map, proving to herself that sometimes traditional methods work best. While she captured stunning sunset shots of the lighthouse, he attempted to teach himself surfing, though Bob ended up spending more time underwater than on the board. The weekend turned out better than either of them expected, with Alice adding amazing photos to her portfolio and Bob, despite his many wipeouts, discovering that he had a newfound respect for the ocean's power.""",
    """Jack first noticed Jill during a company-wide meeting where she was presenting the latest marketing analytics. He found himself impressed not just by her confident delivery, but by how she handled the tough questions from their supervisor, Marcus. While returning to his desk later that day, Jack nearly collided with Jill in the break room, causing her to almost spill her coffee all over herself. The next few weeks saw them frequently crossing paths, as Sarah from HR had assigned them to the same project team. Jill appreciated how Jack always came prepared to meetings, and he admired how she could diffuse tense situations with her quick wit. During one particularly stressful deadline, Jack brought coffee for everyone, remembering exactly how Jill liked hers - a detail that didn't go unnoticed by their teammate Rachel, who gave herself a knowing smile. It wasn't until the annual company picnic that Jack finally worked up the courage to talk to Jill outside of work. While their coworker Tom was organizing the softball game, he found himself gravitating toward where she was setting up the potluck table. Jill had made her famous chocolate chip cookies, and Jack admitted to himself that he had been looking forward to trying them ever since he'd heard Rebecca raving about them at the office. As they talked and laughed through the afternoon, both Jack and Jill realized that their connection went far beyond just being colleagues.""",
    """Jerry and Jimmy had been standing in line for hours with their friends Sally and Emma, determined to get front-row spots at the Crimson Shadows concert. When the doors finally opened, Emma found herself sprinting ahead of the group, her excitement getting the better of her, while Sally tried to keep up with her best friend. The lead singer, Marcus Chen, noticed their enthusiasm from backstage and sent his assistant to invite all four of them to a special pre-show meet-and-greet. Jimmy could hardly contain himself when he realized they'd be meeting not only Marcus but also the legendary guitarist Sarah "Lightning" Rodriguez and drummer Keith Thompson. Sally, who had taught herself to play drums by watching Keith's YouTube videos, was practically shaking as she introduced herself to her idol. Jerry, meanwhile, found himself in an intense conversation with Sarah about vintage guitars, while Emma sneaked photos of herself with each band member. The concert itself was even more magical than they had anticipated. Marcus pulled Sally onto the stage during their hit song "Midnight Rain," letting her play Keith's drums while he took a break to hype up the crowd. Emma screamed herself hoarse as she watched her friend perform, while Jimmy recorded the whole thing on his phone. Jerry caught one of Sarah's guitar picks when she tossed it into the crowd, and he carefully tucked it into his pocket as a souvenir. After the show, Keith invited himself to join their group for late-night pizza, where he shared stories about life on the road. Sally couldn't believe she was casually sharing a pepperoni slice with her drumming hero, while Emma kept pinching herself to make sure she wasn't dreaming. Marcus and Sarah eventually joined them too, and Jimmy found himself teaching Marcus his secret handshake, which the singer promised to use at his next concert. As they finally headed home in the early hours of the morning, Jerry realized he had never seen his friends looking quite so happy, each of them clutching signed merchandise and phones full of photos to prove to themselves that the magical night had really happened.""",
    """At the 2024 Summer Olympics in Paris, records fell across multiple sports as athletes pushed the boundaries of human achievement. Inside the Stade de France, sprinters blazed down the track while pole vaulters soared to new heights. Over at the La Défense Arena, swimmers cut through the water with unprecedented speed, shattering world records in multiple events. The gymnastics competition at Bercy Arena showcased gravity-defying routines on every apparatus, while the climbing walls at Le Bourget tested the limits of speed, strength, and strategy. Beach volleyball matches at the iconic Eiffel Tower stadium drew massive crowds, creating an electric atmosphere in the heart of the city. At the Vélodrome National, cycling records tumbled as competitors pushed the pace to extremes. The streets of Paris transformed into race courses for the marathon and road cycling events, with spectators lining the routes from start to finish. Inside the Porte de la Chapelle Arena, boxing matches kept audiences on the edge of seats, while the breaking competition brought Olympic history with its debut as a medal sport. Throughout the games, the Olympic Village buzzed with energy as athletes from over 200 nations came together in celebration of sport, determination, and international unity."""
]


def main():
    config = DeidentificationConfig(
        replacement="[REDACTED]",
        excluded_entities={"Michael", "Marcus Chen"},
        debug=False
    )

    deidentifier = Deidentification(config)
    for story in STORIES:
        text = deidentifier.deidentify(story)
        elements = deidentifier.get_identified_elements()
        entities = [person["text"] for person in elements["entities"]]
        pronouns = [pronoun["text"] for pronoun in elements["pronouns"]]

        print()
        print(text)
        print("-" * 10)
        print(f"{entities=}")
        print(f"{pronouns=}")
        print()
        print("="*77)


if __name__ == "__main__":
    main()
