"""
Proiect Python - Simulare Joc Solitaire

"""
from typing import Optional

import random
import arcade

# Titlu si dimensiunile ferestrei
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
SCREEN_TITLE = "Joc Solitaire"

# Dimensiunea cartilor
CARD_SCALE = 0.6
CARD_WIDTH = 140 * CARD_SCALE
CARD_HEIGHT = 190 * CARD_SCALE

# Dimensiunile "covorasului" de sub carti 
MAT_PERCENT_OVERSIZE = 1.25
MAT_HEIGHT = int(CARD_HEIGHT * MAT_PERCENT_OVERSIZE)
MAT_WIDTH = int(CARD_WIDTH * MAT_PERCENT_OVERSIZE)

# Spatiul dintre covorase ( in %)
VERTICAL_MARGIN_PERCENT = 0.10
HORIZONTAL_MARGIN_PERCENT = 0.10

# Cordonata Y a ultimlului rand
BOTTOM_Y = MAT_HEIGHT / 2 + MAT_HEIGHT * VERTICAL_MARGIN_PERCENT

# Cordonata X de unde incepem sa plasam obiecte
START_X = MAT_WIDTH / 2 + MAT_WIDTH * HORIZONTAL_MARGIN_PERCENT

# Cordonata Y a primului rand
TOP_Y = SCREEN_HEIGHT - MAT_HEIGHT / 2 - MAT_HEIGHT * VERTICAL_MARGIN_PERCENT

# Cordonata Y al celui de al doilea rand
MIDDLE_Y = TOP_Y - MAT_HEIGHT - MAT_HEIGHT * VERTICAL_MARGIN_PERCENT

# Spatiul dintre teancuri
X_SPACING = MAT_WIDTH + MAT_WIDTH * HORIZONTAL_MARGIN_PERCENT

# Culorile si valorile unor carti de joc
CARD_VALUES = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
CARD_SUITS = ["Clubs", "Hearts", "Spades", "Diamonds"]

# Offset pentru cartile plasate una peste alta
CARD_VERTICAL_OFFSET = CARD_HEIGHT * CARD_SCALE * 0.3

# Imagine carte intoarsa
# Libraria arcade vine cu imagini pentru carti de joc.
FACE_DOWN_IMAGE = ":resources:images/cards/cardBack_red2.png"

# Indexarea diferitelor teancuri folosite in joc
PILE_COUNT = 13
BOTTOM_FACE_DOWN_PILE = 0
BOTTOM_FACE_UP_PILE = 1
PLAY_PILE_1 = 2
PLAY_PILE_2 = 3
PLAY_PILE_3 = 4
PLAY_PILE_4 = 5
PLAY_PILE_5 = 6
PLAY_PILE_6 = 7
PLAY_PILE_7 = 8
TOP_PILE_1 = 9
TOP_PILE_2 = 10
TOP_PILE_3 = 11
TOP_PILE_4 = 12


# un Sprite este un bitmap bidimensional (imagine) care este integrat într-o scenă mai mare, cel mai adesea într-un joc video 2D. - Wikipedia

class Card(arcade.Sprite):
    """ Sprite Carte """

    def __init__(self, suit, value, scale=1):
        """ Constructor Carte """
        self.suit = suit
        self.value = value

        # Imagine carti in functie de culoare si valoare. 
        self.image_file_name = f":resources:images/cards/card{self.suit}{self.value}.png"
        self.is_face_up = False
        super().__init__(FACE_DOWN_IMAGE, scale, hit_box_algorithm="None")

    def face_down(self):
        """ Intoarce cartea pe dos """
        self.texture = arcade.load_texture(FACE_DOWN_IMAGE)
        self.is_face_up = False

    def face_up(self):
        """ Intoarce cartea pe fata """
        self.texture = arcade.load_texture(self.image_file_name)
        self.is_face_up = True

    @property
    def is_face_down(self):
        """ Este cartea intoarsa pe jos? """
        return not self.is_face_up


class MyGame(arcade.Window):
    """ Functia main a jocului """

    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # Lista cu sprite-urile cartilor
        self.card_list: Optional[arcade.SpriteList] = None

        arcade.set_background_color(arcade.color.AMAZON)

        # Lista de carti pe care le mutam cu cursorul
        self.held_cards = None

        # Pozitia originara a cartilor in mutare
        self.held_cards_original_position = None

        # Lista cu sprite-urile covoraselor
        self.pile_mat_list = None

        # Lista de teancuri
        self.piles = None

    def setup(self):
        """ Pentru pregatirea jocului. Apelati functia si pentru a restarta jocul. """

        # Lista de carti pe care le mutam cu cursorul
        self.held_cards = []

        # Pozitia originara a cartilor in mutare
        self.held_cards_original_position = []

        # --- Instantiem covorasele.

        # Lista cu sprite-urile covoraselor
        self.pile_mat_list: arcade.SpriteList = arcade.SpriteList()

        # Cream covorasele
        pile = arcade.SpriteSolidColor(MAT_WIDTH, MAT_HEIGHT, arcade.csscolor.DARK_OLIVE_GREEN)
        pile.position = START_X, BOTTOM_Y
        self.pile_mat_list.append(pile)

        pile = arcade.SpriteSolidColor(MAT_WIDTH, MAT_HEIGHT, arcade.csscolor.DARK_OLIVE_GREEN)
        pile.position = START_X + X_SPACING, BOTTOM_Y
        self.pile_mat_list.append(pile)

        # Cream teancurile din mijloc
        for i in range(7):
            pile = arcade.SpriteSolidColor(MAT_WIDTH, MAT_HEIGHT, arcade.csscolor.DARK_OLIVE_GREEN)
            pile.position = START_X + i * X_SPACING, MIDDLE_Y
            self.pile_mat_list.append(pile)

        # Cream teancurile de sus
        for i in range(4):
            pile = arcade.SpriteSolidColor(MAT_WIDTH, MAT_HEIGHT, arcade.csscolor.DARK_OLIVE_GREEN)
            pile.position = START_X + i * X_SPACING, TOP_Y
            self.pile_mat_list.append(pile)

        # --- Cream, amestecam si impartim cartile.

        self.card_list = arcade.SpriteList()

        for card_suit in CARD_SUITS:
            for card_value in CARD_VALUES:
                card = Card(card_suit, card_value, CARD_SCALE)
                card.position = START_X, BOTTOM_Y
                self.card_list.append(card)

        # Amestecam cartile
        for pos1 in range(len(self.card_list)):
            pos2 = random.randrange(len(self.card_list))
            self.card_list.swap(pos1, pos2)

        # Create a list of lists, each holds a pile of cards.
        self.piles = [[] for _ in range(PILE_COUNT)]

        for card in self.card_list:
            self.piles[BOTTOM_FACE_DOWN_PILE].append(card)

        # - Aranjam cartile in randul din mijloc, cu fata in jos.
        for pile_no in range(PLAY_PILE_1, PLAY_PILE_7 + 1):
            for j in range(pile_no - PLAY_PILE_1 + 1):
                card = self.piles[BOTTOM_FACE_DOWN_PILE].pop()
                self.piles[pile_no].append(card)
                card.position = self.pile_mat_list[pile_no].position
                self.pull_to_top(card)

        # Intoarcem cartile de deasupra.
        for i in range(PLAY_PILE_1, PLAY_PILE_7 + 1):
            self.piles[i][-1].face_up()

    def on_draw(self):
        """ Afisam pe ecran """
        # Curatam ecranul
        self.clear()

        # Covorase
        self.pile_mat_list.draw()

        # Carti
        self.card_list.draw()

    def pull_to_top(self, card: arcade.Sprite):
        """ Punem cartea astfel incat sa apara peste sprite-urile celorlalte """

        self.card_list.remove(card)
        self.card_list.append(card)

    def on_key_press(self, symbol: int, modifiers: int):
        """ Jucatorul apasa o tasta """
        if symbol == arcade.key.R:
            # restart
            self.setup()

    def on_mouse_press(self, x, y, button, key_modifiers):
        """ Jucatorul apasa pe mouse """
        cards = arcade.get_sprites_at_point((x, y), self.card_list)

        # A apasat pe o carte?
        if len(cards) > 0:

            # Daca e un teanc, ia-o pe prima
            primary_card = cards[-1]
            assert isinstance(primary_card, Card)

            # Ne dam seama in ce teanc se afla
            pile_index = self.get_pile_for_card(primary_card)

            # Dam click pe pachetul de jos?
            if pile_index == BOTTOM_FACE_DOWN_PILE:
                # Intoarce 3 carti
                for i in range(3):
                    # Daca nu mai avem carti, oprestete
                    if len(self.piles[BOTTOM_FACE_DOWN_PILE]) == 0:
                        break
                    # Ia cartea de sus
                    card = self.piles[BOTTOM_FACE_DOWN_PILE][-1]
                    # Intoarce-o cu fata in sus
                    card.face_up()
                    card.position = self.pile_mat_list[BOTTOM_FACE_UP_PILE].position
                    # Scoate-o din lista cartilor cu fata in jos 
                    self.piles[BOTTOM_FACE_DOWN_PILE].remove(card)
                    # Adaug-o in lista cartilor cu fata in sus
                    self.piles[BOTTOM_FACE_UP_PILE].append(card)
                    self.pull_to_top(card)

            elif primary_card.is_face_down:
                # daca prima carte din cele 7 teancuri e cu fata in jos, intoarce-o
                primary_card.face_up()
            else:
                # Altfel, ia cartea pe care dam click
                self.held_cards = [primary_card]
                # Salveaza-i pozitia
                self.held_cards_original_position = [self.held_cards[0].position]
                
                self.pull_to_top(self.held_cards[0])

                # Daca e un teanc, ia-l pe tot
                card_index = self.piles[pile_index].index(primary_card)
                for i in range(card_index + 1, len(self.piles[pile_index])):
                    card = self.piles[pile_index][i]
                    self.held_cards.append(card)
                    self.held_cards_original_position.append(card.position)
                    self.pull_to_top(card)

        else:

            # A dat click pe covoras?
            mats = arcade.get_sprites_at_point((x, y), self.pile_mat_list)

            if len(mats) > 0:
                mat = mats[0]
                mat_index = self.pile_mat_list.index(mat)

                # e covorasul de jos, fara carti in el?
                if mat_index == BOTTOM_FACE_DOWN_PILE and len(self.piles[BOTTOM_FACE_DOWN_PILE]) == 0:
                    # incepe sa treci din nou prin pachetul de carti
                    temp_list = self.piles[BOTTOM_FACE_UP_PILE].copy()
                    for card in reversed(temp_list):
                        card.face_down()
                        self.piles[BOTTOM_FACE_UP_PILE].remove(card)
                        self.piles[BOTTOM_FACE_DOWN_PILE].append(card)
                        card.position = self.pile_mat_list[BOTTOM_FACE_DOWN_PILE].position

    def remove_card_from_pile(self, card):
        """ Scoate cartea din teanc """
        for pile in self.piles:
            if card in pile:
                pile.remove(card)
                break

    def get_pile_for_card(self, card):
        """ In ce teanc e cartea asta ? """
        for index, pile in enumerate(self.piles):
            if card in pile:
                return index

    def move_card_to_new_pile(self, card, pile_index):
        """ Muta cartea intr-un nou teanc """
        self.remove_card_from_pile(card)
        self.piles[pile_index].append(card)

    def on_mouse_release(self, x: float, y: float, button: int,
                         modifiers: int):
        """ Cand jucatorul apasa pe mouse """

        # Daca nu mai avem carti, nu face nimic
        if len(self.held_cards) == 0:
            return

        # Daca apasam pe mai multe, ia-o pe cea mai apropiata de cursor
        pile, distance = arcade.get_closest_sprite(self.held_cards[0], self.pile_mat_list)
        reset_position = True

        if arcade.check_for_collision(self.held_cards[0], pile):

            # din ce teanc face parte?
            pile_index = self.pile_mat_list.index(pile)

            # teancul destinatie e la fel cu cel din care am luat cartea?
            if pile_index == self.get_pile_for_card(self.held_cards[0]):
                # daca da, nu facem nimic
                pass

            # face parte din teancurile din mijloc?
            elif PLAY_PILE_1 <= pile_index <= PLAY_PILE_7:
                # sunt deja carti acolo?
                if len(self.piles[pile_index]) > 0:
                    # muta cartile
                    top_card = self.piles[pile_index][-1]
                    for i, dropped_card in enumerate(self.held_cards):
                        dropped_card.position = top_card.center_x, \
                                                top_card.center_y - CARD_VERTICAL_OFFSET * (i + 1)
                else:
                    #nu sunt carti?
                    for i, dropped_card in enumerate(self.held_cards):
                        # muta cartile unde trebuie
                        dropped_card.position = pile.center_x, \
                                                pile.center_y - CARD_VERTICAL_OFFSET * i

                for card in self.held_cards:
                    self.move_card_to_new_pile(card, pile_index)

                # succes, nu resetam pozitia cartilor
                reset_position = False

            # daca mutam o singura carte deasupra unui teanc
            elif TOP_PILE_1 <= pile_index <= TOP_PILE_4 and len(self.held_cards) == 1:
                self.held_cards[0].position = pile.position
                for card in self.held_cards:
                    self.move_card_to_new_pile(card, pile_index)

                reset_position = False

        if reset_position:
            # punem cartile inapoi de unde le-am luat
            for pile_index, card in enumerate(self.held_cards):
                card.position = self.held_cards_original_position[pile_index]

        # nu mai tinem carti in mana
        self.held_cards = []

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        """ Jucatorul misca mouse-ul """

        # daca tinem carti, muta-le cu cursorul
        for card in self.held_cards:
            card.center_x += dx
            card.center_y += dy


def main():
    """ Functia main """
    window = MyGame()
    window.setup()
    arcade.run()


# daca programul e rulat direct, se incepe de aici 
if __name__ == "__main__":
    main()
