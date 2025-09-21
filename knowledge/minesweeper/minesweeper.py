import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        return self.cells if len(self.cells) == self.count else set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        return self.cells if self.count == 0 else set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells -= {cell}
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells -= {cell}


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge: list[Sentence] = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        self.moves_made.add(cell)
        self.mark_safe(cell)

        a_nearby_cells = self.nearby_cells(cell)
        if count == 0:
            for cell in a_nearby_cells:
                self.mark_safe(cell)

        if count > 0:
            sentence = Sentence(a_nearby_cells, count)
            if sentence in self.knowledge:
                return
            self.knowledge.append(sentence)

        self.update_knowledge_base()

        new_safes = self.find_new_safes()
        new_mines = self.find_new_mines()
        loop_counter = 0

        while ((len(new_safes) > 0 or len(new_mines) > 0)
               and loop_counter < 150):
            print(f"new_safes: {new_safes}")
            print(f"new_mines: {new_mines}")

            loop_counter += 1
            if len(new_safes) > 0:
                for cell in new_safes:
                    self.mark_safe(cell)

            if len(new_mines) > 0:
                for cell in new_mines:
                    self.mark_mine(cell)

            self.update_knowledge_base()

            new_safes = self.find_new_safes()
            new_mines = self.find_new_mines()

        print(f"breaker: {loop_counter}")
        for i, sentence in enumerate(self.knowledge):
            print(f"knowledge {i}: {self.knowledge[i]}")
        print(f"all safe moves: {self.safes}")
        print(f"all mines: {self.mines}")

    def find_new_safes(self):
        new_safes = set()
        for sentence in self.knowledge:
            kn_safes = sentence.known_safes()
            if len(kn_safes) > 0:
                new_safes |= kn_safes
        return new_safes

    def find_new_mines(self):
        new_mines = set()
        for sentence in self.knowledge:
            kn_mines = sentence.known_mines()
            if len(kn_mines) > 0:
                new_mines |= kn_mines
        new_mines -= self.mines
        return new_mines

    def nearby_cells(self, cell):
        return {(i, j)
                for i in range(cell[0] - 1, cell[0] + 2)
                for j in range(cell[1] - 1, cell[1] + 2)
                if (i, j) != cell and 0 <= i < self.width and 0 <= j < self.height}

    def new_sentence_from_safes(self, current_sentence):
        delta = current_sentence.cells - self.safes
        if delta < current_sentence.cells and len(delta) > 0:
            sentence = Sentence(delta, current_sentence.count)
            if sentence not in self.knowledge and len(sentence.cells) > 0:
                return sentence
        return None

    def update_knowledge_base(self):
        print(f"update_knowledge_base started")
        self.knowledge = [snt for snt in self.knowledge if len(snt.cells) > 0]

        no_doubles = []

        for snt in self.knowledge:
            if snt not in no_doubles:
                no_doubles.append(snt)
        self.knowledge = no_doubles

        for_adding = []
        for i in range(len(self.knowledge) - 1):
            for j in range(i + 1, len(self.knowledge)):
                sentence1 = self.knowledge[i]
                sentence2 = self.knowledge[j]
                for sentence in (self.new_sentence_from_safes(sentence1), self.new_sentence_from_safes(sentence2)):
                    if sentence is not None and sentence not in for_adding:
                        for_adding.append(sentence)

                new_sentence = None

                if sentence1.cells.issubset(sentence2.cells):
                    new_sentence = Sentence(sentence2.cells - sentence1.cells,
                                            sentence2.count - sentence1.count)
                elif sentence2.cells.issubset(sentence1.cells):
                    new_sentence = Sentence(sentence1.cells - sentence2.cells,
                                            sentence1.count - sentence2.count)

                if (new_sentence is not None
                        and new_sentence not in self.knowledge
                        and new_sentence not in for_adding
                        and len(new_sentence.cells) > 0):
                    for_adding.append(new_sentence)

        for item in for_adding:
            print(f"for adding: {item}")

        if len(for_adding) > 0:
            for sentence in for_adding:
                self.knowledge.append(sentence)
            print("knowledge recursive update is needed")
            self.update_knowledge_base()

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        available_moves = self.safes - self.moves_made

        if len(available_moves) > 0:
            return random.choice(list(available_moves))
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        available_moves = {(i, j) for i in range(self.width)
                           for j in range(self.height)} - self.moves_made - self.mines
        if len(available_moves) > 0:
            return random.choice(list(available_moves))
        return None
