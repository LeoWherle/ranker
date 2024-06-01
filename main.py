"""A simple pairwise ranking app using tkinter."""

import json
import os
import tkinter as tk

from PIL import Image, ImageDraw, ImageTk


class ElementManager:
    """A class to manage elements."""

    def __init__(self, json_path, image_size=200):
        self.image_size = image_size
        self.elements = self.load_elements(json_path)

    def load_elements(self, json_path):
        """Load the elements from a JSON file.

        Example JSON file:
        [
            {
                "title": "Element A",
                "description": "This is element A",
                "image": "images/element_a.png"
            },
            {
                "title": "Element B",
                "description": "This is element B",
                "image": "images/element_b.png"
            }
        ]

        Parameters:
        json_path (str): The path to the JSON file.

        Returns:
        list: The list of elements.
        """
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def load_image(self, path):
        """Load an image from a file.

        Args:
            path (str): The path to the image file.

        Returns:
            PhotoImage: The image.
        """
        if os.path.exists(path):
            image = Image.open(path)
            image = image.resize((self.image_size, self.image_size))
        else:
            image = Image.new("RGB", (self.image_size, self.image_size), color="purple")
            draw = ImageDraw.Draw(image)
            draw.text(
                (self.image_size // 4, self.image_size // 2), "No Image", fill="white"
            )
        return ImageTk.PhotoImage(image)


class PairwiseComparator:
    """A class to compare elements pairwise."""

    def __init__(self, elements):
        self.elements = elements
        self.n = len(elements)
        self.pairs = [(i, j) for i in range(self.n) for j in range(i + 1, self.n)]
        self.index = 0
        self.rankings = [0] * self.n

    def next_pair(self):
        """Get the next pair of elements to compare.

        Returns:
            tuple: A pair of indices of the elements to compare.
        """
        if self.index < len(self.pairs):
            return self.pairs[self.index]
        else:
            return None

    def update_ranking(self, winner):
        """Update the ranking based on the winner of the comparison.

        Parameters:
            winner (int): The index of the winner element.
        """
        self.rankings[winner] += 1
        self.index += 1

    def get_rankings(self):
        """Get the rankings of the elements.

        Returns:
            list: The ranked elements.
        """
        return [
            x
            for _, x in sorted(
                zip(self.rankings, self.elements),
                key=lambda pair: pair[0],
                reverse=True,
            )
        ]


class PairwiseRankingApp:
    """A class to create a pairwise ranking app using tkinter."""
    def __init__(self, tkroot, elem_manager, comparator_c):
        self.root = tkroot
        self.element_manager = elem_manager
        self.comparator = comparator_c

        self.label = tk.Label(tkroot, text="Which one do you prefer?")
        self.label.pack()

        self.frame1 = tk.Frame(tkroot)
        self.frame1.pack(side="left", padx=20, pady=20)

        self.frame2 = tk.Frame(tkroot)
        self.frame2.pack(side="right", padx=20, pady=20)

        self.button1 = tk.Button(self.frame1, command=self.choose_first)
        self.button1.pack()

        self.button2 = tk.Button(self.frame2, command=self.choose_second)
        self.button2.pack()

        self.result = tk.Label(tkroot, text="")

        self.update_buttons()

    def update_buttons(self):
        """Update the buttons with the next pair of elements."""
        pair = self.comparator.next_pair()
        if pair is not None:
            i, j = pair

            # Update left element
            element1 = self.element_manager.elements[i]
            image1 = self.element_manager.load_image(element1["image"])
            self.button1.config(
                image=image1,
                text=element1["title"] + "\n\n" + element1["description"],
                compound="top",
            )
            self.button1.image = image1  # keep a reference to avoid garbage collection

            # Update right element
            element2 = self.element_manager.elements[j]
            image2 = self.element_manager.load_image(element2["image"])
            self.button2.config(
                image=image2,
                text=element2["title"] + "\n\n" + element2["description"],
                compound="top",
            )
            self.button2.image = image2  # keep a reference to avoid garbage collection
        else:
            # kill the old window and display the results
            self.frame1.destroy()
            self.frame2.destroy()
            self.label.destroy()
            self.display_results()

    def choose_first(self):
        """Update the ranking based on the first choice."""
        self.comparator.update_ranking(self.comparator.next_pair()[0])
        self.update_buttons()

    def choose_second(self):
        """Update the ranking based on the second choice."""
        self.comparator.update_ranking(self.comparator.next_pair()[1])
        self.update_buttons()

    def display_results(self):
        """Display the results of the ranking."""
        sorted_elements = self.comparator.get_rankings()
        self.result.config(text="Ranking:")
        self.result.pack()

        # Resize the existing window for displaying the rankings
        self.root.geometry("600x800")

        # Create a canvas with a scrollbar
        canvas = tk.Canvas(self.root)
        scrollbar = tk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        # Create a frame inside the canvas for the rankings
        rankings_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=rankings_frame, anchor="nw")

        # Display the rankings
        for i, element in enumerate(sorted_elements):
            # Load the image
            image = self.element_manager.load_image(element["image"])

            # Create a label for the image
            image_label = tk.Label(rankings_frame, image=image)
            image_label.image = image
            image_label.grid(row=i, column=0, padx=10, pady=10)

            # Create a label for the title and description
            title_label = tk.Label(
                rankings_frame, text=element["title"], font=("Arial", 12, "bold")
            )
            title_label.grid(row=i, column=1, sticky="w", padx=10)

            description_label = tk.Label(
                rankings_frame, text=element["description"], wraplength=300
            )
            description_label.grid(row=i, column=2, sticky="w", padx=10, pady=5)

        # Configure the canvas to scroll
        rankings_frame.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))


if __name__ == "__main__":
    element_manager = ElementManager("elements.json")
    comparator = PairwiseComparator(element_manager.elements)

    root = tk.Tk()
    app = PairwiseRankingApp(root, element_manager, comparator)
    root.mainloop()
