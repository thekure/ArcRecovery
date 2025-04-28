from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene
from PyQt5.QtGui import QPen, QBrush, QColor, QFont, QPainter
from PyQt5.QtCore import Qt
import networkx as nx

class GraphView(QGraphicsView):
    def __init__(self, graph, parent=None):
        try:
            super().__init__(parent)
            print(f"Initializing GraphView with {len(graph.nodes())} nodes and {len(graph.edges())} edges")
            
            if not isinstance(graph, nx.Graph):
                raise ValueError("Input must be a NetworkX graph")
                
            if len(graph.nodes()) == 0:
                raise ValueError("Cannot visualize an empty graph")
                
            print("Creating scene...")
            self.scene = QGraphicsScene(self)
            self.setScene(self.scene)
            self.graph = graph
            self.setRenderHint(QPainter.Antialiasing)
            self.setRenderHint(QPainter.TextAntialiasing)
            
            # Enable dragging and proper view handling
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
            self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
            self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
            
            print("Scene created, calling draw_graph...")
            self.draw_graph()
            
            # Fit the view to show all items
            self.fitInView(self.scene.itemsBoundingRect(), Qt.KeepAspectRatio)
            
        except Exception as e:
            print(f"Error in GraphView.__init__: {str(e)}")
            raise

    def wheelEvent(self, event):
        # Zoom in/out with mouse wheel
        factor = 1.2
        if event.angleDelta().y() < 0:
            factor = 1.0 / factor
        
        # Get the position before scaling
        old_pos = self.mapToScene(event.pos())
        
        # Scale the view
        self.scale(factor, factor)
        
        # Get the position after scaling
        new_pos = self.mapToScene(event.pos())
        
        # Move the scene to keep the mouse position fixed
        delta = new_pos - old_pos
        self.translate(delta.x(), delta.y())

    def draw_graph(self):
        try:
            print("Starting layout calculation...")
            # Use simple spring layout with fewer iterations for testing
            pos = nx.spring_layout(self.graph, iterations=10)
            print("Layout calculated successfully")
            
            print("Starting node drawing...")
            # Draw nodes
            for i, (node, (x, y)) in enumerate(pos.items()):
                if i % 100 == 0:
                    print(f"Drawing node {i}/{len(pos)}")
                try:
                    # Simple node drawing
                    ellipse = self.scene.addEllipse(
                        x * 500, 
                        y * 500, 
                        20, 
                        20,
                        QPen(Qt.black, 1),
                        QBrush(QColor(200, 200, 255))
                    )
                    
                    # Simple label
                    label = self.scene.addText(str(node))
                    label.setFont(QFont("Arial", 8))
                    label.setPos(x * 500 + 10, y * 500 + 20)
                except Exception as e:
                    print(f"Error drawing node {node}: {str(e)}")
                    raise
            
            print("Nodes drawn, starting edge drawing...")
            # Draw edges
            for i, (src, dst) in enumerate(self.graph.edges()):
                if i % 100 == 0:
                    print(f"Drawing edge {i}/{len(self.graph.edges())}")
                try:
                    if src in pos and dst in pos:
                        src_x, src_y = pos[src]
                        dst_x, dst_y = pos[dst]
                        self.scene.addLine(
                            src_x * 500 + 10, 
                            src_y * 500 + 10, 
                            dst_x * 500 + 10, 
                            dst_y * 500 + 10, 
                            QPen(Qt.black)
                        )
                except Exception as e:
                    print(f"Error drawing edge {src}->{dst}: {str(e)}")
                    raise
            
            print("Graph drawn successfully")
            # Set scene rect to include all items
            self.scene.setSceneRect(self.scene.itemsBoundingRect())
            
        except Exception as e:
            print(f"Error in draw_graph: {str(e)}")
            raise ValueError(f"Error drawing graph: {str(e)}") 