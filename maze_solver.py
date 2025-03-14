import numpy as np
import heapq
import matplotlib.pyplot as plt

class MazeSolver:
    """Solve mazes using the A* algorithm."""
    
    def __init__(self, maze):
        """Initialize the solver with a maze.
        
        Args:
            maze: A numpy array where 0 represents paths and 1 represents walls.
        """
        self.maze = maze
        self.height, self.width = maze.shape
        self.start = None
        self.end = None
        self.solution_path = None
        self.explored_cells = None
    
    def set_start_end(self, start=None, end=None):
        """Set the start and end points for the maze.
        
        If not provided, defaults to top-left and bottom-right corners.
        
        Args:
            start: Tuple (row, col) for the start position
            end: Tuple (row, col) for the end position
        """
        # Default start is the top-left corner (first path cell)
        if start is None:
            for j in range(1, self.width):
                if self.maze[1, j] == 0:  # Find first open path in top row
                    self.start = (1, j)
                    break
            if self.start is None:  # If no open path in top row, use first open cell
                for i in range(1, self.height, 2):
                    for j in range(1, self.width, 2):
                        if self.maze[i, j] == 0:
                            self.start = (i, j)
                            break
                    if self.start is not None:
                        break
        else:
            self.start = start
        
        # Default end is the bottom-right corner (last path cell)
        if end is None:
            for j in range(self.width-2, 0, -1):
                if self.maze[self.height-2, j] == 0:  # Find last open path in bottom row
                    self.end = (self.height-2, j)
                    break
            if self.end is None:  # If no open path in bottom row, use last open cell
                for i in range(self.height-2, 0, -2):
                    for j in range(self.width-2, 0, -2):
                        if self.maze[i, j] == 0:
                            self.end = (i, j)
                            break
                    if self.end is not None:
                        break
        else:
            self.end = end
    
    def heuristic(self, a, b):
        """Calculate the Manhattan distance heuristic between points a and b."""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    
    def get_neighbors(self, position):
        """Get all valid neighboring positions (up, right, down, left)."""
        row, col = position
        neighbors = []
        
        # Check all four directions
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # right, down, left, up
        
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            
            # Check if the new position is within bounds and is a path (not a wall)
            if (0 <= new_row < self.height and 0 <= new_col < self.width and 
                    self.maze[new_row, new_col] == 0):
                neighbors.append((new_row, new_col))
        
        return neighbors
    
    def solve(self, bidirectional=True, callback=None, algorithm='astar'):
        """Solve the maze using the specified algorithm.
        
        Args:
            bidirectional: If True, use bidirectional search for better performance.
            callback: Optional function to call after each step for visualization.
            algorithm: The algorithm to use ('astar', 'dijkstra', 'bfs', 'dfs').
            
        Returns:
            A list of coordinates representing the solution path,
            or None if no solution exists.
        """
        # Wrap callback to reduce animation frequency
        animation_counter = 0
        def animation_callback(maze):
            nonlocal animation_counter
            animation_counter += 1
            if callback and animation_counter % 5 == 0:  # Update every 5th step
                callback(maze)
        
        if algorithm == 'bfs':
            return self._solve_bfs(animation_callback if callback else None)
        elif algorithm == 'dfs':
            return self._solve_dfs(animation_callback if callback else None)
        elif algorithm == 'dijkstra':
            return self._solve_dijkstra(animation_callback if callback else None)
        else:  # Default to A*
            return self._solve_astar(bidirectional, animation_callback if callback else None)
    
    def _solve_bfs(self, callback=None):
        """Solve the maze using Breadth-First Search."""
        if self.start is None or self.end is None:
            self.set_start_end()
        
        queue = [(self.start, [self.start])]
        visited = {self.start}
        self.explored_cells = set()
        
        while queue:
            current, path = queue.pop(0)
            self.explored_cells.add(current)
            
            if callback:
                callback(self.get_solution_maze())
            
            if current == self.end:
                self.solution_path = path
                return path
            
            for neighbor in self.get_neighbors(current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        
        return None
    
    def _solve_dfs(self, callback=None):
        """Solve the maze using Depth-First Search."""
        if self.start is None or self.end is None:
            self.set_start_end()
        
        stack = [(self.start, [self.start])]
        visited = {self.start}
        self.explored_cells = set()
        
        while stack:
            current, path = stack.pop()
            self.explored_cells.add(current)
            
            if callback:
                callback(self.get_solution_maze())
            
            if current == self.end:
                self.solution_path = path
                return path
            
            for neighbor in reversed(self.get_neighbors(current)):
                if neighbor not in visited:
                    visited.add(neighbor)
                    stack.append((neighbor, path + [neighbor]))
        
        return None
    
    def _solve_dijkstra(self, callback=None):
        """Solve the maze using Dijkstra's algorithm."""
        if self.start is None or self.end is None:
            self.set_start_end()
        
        distances = {self.start: 0}
        came_from = {}
        pq = [(0, self.start)]
        self.explored_cells = set()
        
        while pq:
            current_dist, current = heapq.heappop(pq)
            
            if current == self.end:
                path = [current]
                while current in came_from:
                    current = came_from[current]
                    path.append(current)
                path.reverse()
                self.solution_path = path
                return path
            
            self.explored_cells.add(current)
            
            if callback:
                callback(self.get_solution_maze())
            
            for neighbor in self.get_neighbors(current):
                dist = current_dist + 1
                
                if neighbor not in distances or dist < distances[neighbor]:
                    distances[neighbor] = dist
                    came_from[neighbor] = current
                    heapq.heappush(pq, (dist, neighbor))
        
        return None
    
    def _solve_astar(self, bidirectional=True, callback=None):
        if self.start is None or self.end is None:
            self.set_start_end()
        
        # Initialize forward and backward search
        fwd_open = []
        back_open = []
        fwd_closed = set()
        back_closed = set()
        
        # Dictionaries for path reconstruction
        fwd_came_from = {}
        back_came_from = {}
        
        # Cost dictionaries
        fwd_g = {self.start: 0}
        back_g = {self.end: 0}
        fwd_f = {self.start: self.heuristic(self.start, self.end)}
        back_f = {self.end: self.heuristic(self.end, self.start)}
        
        # Add start/end nodes to respective open sets
        heapq.heappush(fwd_open, (fwd_f[self.start], self.start))
        if bidirectional:
            heapq.heappush(back_open, (back_f[self.end], self.end))
        
        # To track explored cells for visualization
        self.explored_cells = set()
        
        def process_node(current, open_set, closed_set, came_from, g_score, f_score, is_forward):
            neighbors = self.get_neighbors(current)
            target = self.end if is_forward else self.start
            other_closed = back_closed if is_forward else fwd_closed
            
            for neighbor in neighbors:
                if neighbor in closed_set:
                    continue
                
                tentative_g = g_score.get(current, float('inf')) + 1
                
                if neighbor not in [i[1] for i in open_set] or tentative_g < g_score.get(neighbor, float('inf')):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + self.heuristic(neighbor, target)
                    
                    if neighbor not in [i[1] for i in open_set]:
                        heapq.heappush(open_set, (f_score[neighbor], neighbor))
                    
                    # Check if we've found a path
                    if neighbor in other_closed:
                        return neighbor
            return None
        
        while fwd_open and (not bidirectional or back_open):
            # Process forward search
            if fwd_open:
                current_f, current = heapq.heappop(fwd_open)
                
                if current == self.end:
                    # Found path in forward search
                    path = [current]
                    while current in fwd_came_from:
                        current = fwd_came_from[current]
                        path.append(current)
                    path.reverse()
                    self.solution_path = path
                    return path
                
                fwd_closed.add(current)
                self.explored_cells.add(current)
                
                # Update visualization if callback provided
                if callback:
                    callback(self.get_solution_maze())
                
                # Process forward neighbors
                meeting_point = process_node(current, fwd_open, fwd_closed, fwd_came_from,
                                           fwd_g, fwd_f, True)
                if meeting_point:
                    # Reconstruct path from both directions
                    fwd_path = [meeting_point]
                    current = meeting_point
                    while current in fwd_came_from:
                        current = fwd_came_from[current]
                        fwd_path.append(current)
                    fwd_path.reverse()
                    
                    back_path = []
                    current = meeting_point
                    while current in back_came_from:
                        current = back_came_from[current]
                        back_path.append(current)
                    
                    self.solution_path = fwd_path + back_path[1:]
                    return self.solution_path
            
            # Process backward search if bidirectional
            if bidirectional and back_open:
                current_f, current = heapq.heappop(back_open)
                
                back_closed.add(current)
                self.explored_cells.add(current)
                
                # Update visualization if callback provided
                if callback:
                    callback(self.get_solution_maze())
                
                # Process backward neighbors
                meeting_point = process_node(current, back_open, back_closed, back_came_from,
                                           back_g, back_f, False)
                if meeting_point:
                    # Reconstruct path from both directions
                    fwd_path = [meeting_point]
                    current = meeting_point
                    while current in fwd_came_from:
                        current = fwd_came_from[current]
                        fwd_path.append(current)
                    fwd_path.reverse()
                    
                    back_path = []
                    current = meeting_point
                    while current in back_came_from:
                        current = back_came_from[current]
                        back_path.append(current)
                    
                    self.solution_path = fwd_path + back_path[1:]
                    return self.solution_path
        
        # If we get here, there's no path
        return None
    
    def get_solution_maze(self):
        """Get a visualization of the solution."""
        if self.maze is None:
            return None
        
        # Create a RGB array for colored visualization
        viz_maze = np.zeros((self.height, self.width, 3))
        
        # Set walls (white) and paths (black)
        viz_maze[self.maze == 1] = [1, 1, 1]  # White for walls
        viz_maze[self.maze == 0] = [0, 0, 0]  # Black for paths
        
        # Color the explored cells (light blue)
        if self.explored_cells:
            for cell in self.explored_cells:
                if self.maze[cell[0], cell[1]] == 0:  # Only color path cells
                    viz_maze[cell[0], cell[1]] = [0.6, 0.8, 1.0]  # Light blue
        
        # Color the solution path (green)
        if self.solution_path:
            for cell in self.solution_path:
                viz_maze[cell[0], cell[1]] = [0.2, 0.8, 0.2]  # Green
        
        # Highlight start (blue) and end (red) points
        if self.start:
            viz_maze[self.start[0], self.start[1]] = [0, 0, 1]  # Blue
        if self.end:
            viz_maze[self.end[0], self.end[1]] = [1, 0, 0]  # Red
        
        return viz_maze
    
    def display_solution(self):
        """Display the maze with the solution path."""
        solution_maze = self.get_solution_maze()
        
        # Create a colormap: black=wall, white=path, red=solution, blue=explored
        cmap = plt.cm.colors.ListedColormap(['white', 'black', 'red', 'lightblue', 'green', 'orange'])
        
        plt.figure(figsize=(10, 10))
        plt.imshow(solution_maze, cmap=cmap)
        plt.axis('off')
        plt.title(f"Maze Solution ({(self.width-1)//2}x{(self.height-1)//2})")
        
        # Add a legend
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='black', edgecolor='black', label='Wall'),
            Patch(facecolor='white', edgecolor='black', label='Path'),
            Patch(facecolor='red', edgecolor='black', label='Solution'),
            Patch(facecolor='lightblue', edgecolor='black', label='Explored'),
            Patch(facecolor='green', edgecolor='black', label='Start'),
            Patch(facecolor='orange', edgecolor='black', label='End')
        ]
        plt.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=3)
        
        plt.show()
    
    def save_solution(self, filename):
        """Save the maze solution as an image."""
        solution_maze = self.get_solution_maze()
        
        # Create a colormap: black=wall, white=path, red=solution, blue=explored
        cmap = plt.cm.colors.ListedColormap(['white', 'black', 'red', 'lightblue', 'green', 'orange'])
        
        plt.figure(figsize=(10, 10))
        plt.imshow(solution_maze, cmap=cmap)
        plt.axis('off')
        plt.title(f"Maze Solution ({(self.width-1)//2}x{(self.height-1)//2})")
        
        # Add a legend
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='black', edgecolor='black', label='Wall'),
            Patch(facecolor='white', edgecolor='black', label='Path'),
            Patch(facecolor='red', edgecolor='black', label='Solution'),
            Patch(facecolor='lightblue', edgecolor='black', label='Explored'),
            Patch(facecolor='green', edgecolor='black', label='Start'),
            Patch(facecolor='orange', edgecolor='black', label='End')
        ]
        plt.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=3)
        
        plt.savefig(filename)
        plt.close()