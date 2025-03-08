from django.test import TestCase
from blog_improved.utils.tree import Tree, BfsIterator, DfsIterator

def create_alphabet_graph():
    graph = Tree(value="a")
    branch_lengths = [6, 3, 5, 1, 8, 2]
    branch_iter = iter(branch_lengths)

    try:
        current_branch = next(branch_iter)  # First branch position
    except StopIteration:
        return graph  # No branches, return the root

    node = graph  # Start at the root
    counter = current_branch
    for i in range(1, 26):
        alphabet_char = chr(97 + i)  # Generate letter (b to y)
        if i > counter:  # Start a new branch
            try:
                current_branch = next(branch_iter)
                counter = counter + current_branch
            except StopIteration:
                pass  # No more branches to start

            # Add a new child to the root
            graph.add_child(alphabet_char)
            node = graph.children[-1]  # Move to the last added child
        else:
            node.add_child(alphabet_char)  # Add to current branch
            node = node.children[-1]

    return graph  # Return the tree for verification

class UtilsTreeTestCase(TestCase):
    def test_dfs_search(self):
        nary_alphabet = create_alphabet_graph()
        last_letter = ""
        for unicode_val, letter in enumerate(DfsIterator(nary_alphabet), start=97):
            expected_letter = chr(unicode_val)
            self.assertTrue( "a" <= letter <= "z")
            self.assertEqual(letter, expected_letter)
            last_letter = letter

        self.assertEqual(last_letter, "z")

    def test_bfs_search_top_row(self):
        nary_alphabet = create_alphabet_graph()
        branch_lengths = [6, 3, 5, 1, 8, 2]
        branch_iter =  iter(branch_lengths)
        try:
            branch = next(branch_iter) 
        except:
            raise StopIteration()
        
        expected_letters = ["a", "b", "h", "k", "p", "q", "y"]  
        self.assertEqual(nary_alphabet.children[0].value, "b")
        self.assertEqual(nary_alphabet.children[1].value, "h")
        self.assertEqual(nary_alphabet.children[2].value, "k")
        self.assertEqual(nary_alphabet.children[3].value, "p")
        self.assertEqual(nary_alphabet.children[4].value, "q")
        self.assertEqual(nary_alphabet.children[5].value, "y")

        for index, letter in enumerate(BfsIterator(nary_alphabet), start=0):
            self.assertTrue( "a" <= letter <= "z")
            if index < len(expected_letters):
                self.assertEqual(letter, expected_letters[index])
            else:
                break
 
