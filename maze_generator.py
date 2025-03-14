import random
import matplotlib.pyplot as plt
import numpy as np

class DisjointSet:
    """A data structure that keeps track of a set of elements partitioned into a number of disjoint subsets."""
    
    def __init__(self, num_elements):
        # Initialize each element as its own parent
        self.parent = list(range(num_elements))
        # Initialize rank (tree height) for each element
        self.rank = [0] * num_elements
    
    def find(self, x):
        """Find the representative (root) of the set containing element x."""
        # Path compression: make each examined node point directly to the root
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]
    
    def union(self, x, y):
        """Merge the sets containing elements x and y."""
        # Find the roots of the sets
        root_x = self.find(x)
        root_y = self.find(y)
        
        # If they're already in the same set, do nothing
        if root_x == root_y:
            return False
        
        # Union by rank: attach the shorter tree to the root of the taller tree
        if self.rank[root_x] < self.rank[root_y]:
            self.parent[root_x] = root_y
        elif self.rank[root_x] > self.rank[root_y]:
            self.parent[root_y] = root_x
        else:
            # If ranks are the same, make one the parent and increment its rank
            self.parent[root_y] = root_x
            self.rank[root_x] += 1
        
        return True

class MazeGenerator:
    """Generate mazes using Kruskal's algorithm."""
    
    def __init__(self, width, height, difficulty='normal'):
        self.width = width
        self.height = height
        self.difficulty = difficulty
        # Initialize maze with all walls
        # 0 = path (no wall), 1 = wall
        # We'll use a grid that's 2*width+1 by 2*height+1 to represent cells and walls
        self.maze = np.ones((2*height+1, 2*width+1), dtype=np.uint8)
        
        # Mark all cells (not walls) as paths
        for i in range(1, 2*height, 2):
            for j in range(1, 2*width, 2):
                self.maze[i, j] = 0
        
        # Animation callback
        self.animation_callback = None
    
    def set_animation_callback(self, callback):
        """Set a callback function for maze generation animation.
        
        Args:
            callback: Function to call with current maze state during generation.
        """
        self.animation_callback = callback
    
    def generate(self):
        """Generate a maze using Kruskal's algorithm.
        
        The difficulty level affects the maze complexity:
        - 'easy': More straight paths, fewer dead ends
        - 'normal': Balanced complexity
        - 'hard': More twists and turns, more dead ends
        """
        # Create a list of all walls between cells
        walls = []
        
        # Horizontal walls
        for i in range(1, 2*self.height, 2):
            for j in range(2, 2*self.width, 2):
                # Wall at (i, j) separates cells at (i, j-1) and (i, j+1)
                cell1 = (i, j-1)
                cell2 = (i, j+1)
                walls.append((i, j, cell1, cell2))
        
        # Vertical walls
        for i in range(2, 2*self.height, 2):
            for j in range(1, 2*self.width, 2):
                # Wall at (i, j) separates cells at (i-1, j) and (i+1, j)
                cell1 = (i-1, j)
                cell2 = (i+1, j)
                walls.append((i, j, cell1, cell2))
        
        # Shuffle the walls to randomize the maze
        random.shuffle(walls)
        
        # Create a disjoint set for all cells
        num_cells = self.width * self.height
        ds = DisjointSet(num_cells)
        
        # Adjust wall selection based on difficulty
        if self.difficulty == 'easy':
            # Sort walls to prefer straight paths
            walls.sort(key=lambda w: abs(w[0] - w[2][0]) + abs(w[1] - w[2][1]))
        elif self.difficulty == 'hard':
            # Additional shuffling for more complexity
            random.shuffle(walls)
            random.shuffle(walls)
        
        # Process each wall
        for wall_i, wall_j, (cell1_i, cell1_j), (cell2_i, cell2_j) in walls:
            # Convert cell coordinates to cell indices
            cell1_idx = (cell1_i // 2) * self.width + (cell1_j // 2)
            cell2_idx = (cell2_i // 2) * self.width + (cell2_j // 2)
            
            # If the cells are not already connected, remove the wall between them
            if ds.union(cell1_idx, cell2_idx):
                self.maze[wall_i, wall_j] = 0
                
                # Call animation callback if set, but only every 50 walls to speed up animation
                if self.animation_callback and len(walls) % 50 == 0:
                    self.animation_callback(self.maze)
        
        return self.maze
    
    def display(self):
        """Display the generated maze."""
        plt.figure(figsize=(10, 10))
        plt.imshow(self.maze, cmap='binary')
        plt.axis('off')
        plt.title(f"Maze ({self.width}x{self.height})")
        plt.show()
    
    def save(self, filename):
        """Save the maze as an image."""
        plt.figure(figsize=(10, 10))
        plt.imshow(self.maze, cmap='binary')
        plt.axis('off')
        plt.title(f"Maze ({self.width}x{self.height})")
        plt.savefig(filename)
        plt.close()

def main():
    # Get maze dimensions from user
    try:
        width = int(input("Enter maze width: "))
        height = int(input("Enter maze height: "))
        
        if width <= 0 or height <= 0:
            print("Dimensions must be positive integers.")
            return
        
        # Generate and display the maze
        generator = MazeGenerator(width, height)
        generator.generate()
        generator.display()
        
        # Ask if user wants to save the maze
        save_option = input("Do you want to save the maze? (y/n): ").lower()
        if save_option == 'y':
            filename = input("Enter filename (e.g., maze.png): ")
            generator.save(filename)
            print(f"Maze saved as {filename}")
    
    except ValueError:
        print("Please enter valid integers for dimensions.")

if __name__ == "__main__":
    main()