import re
from collections import Counter
import networkx as nx
import matplotlib.pyplot as plt
import random
from PyQt5 import QtCore, QtGui, QtWidgets
import time
import threading
import matplotlib.image as mpimg

count = 0
path_random=[]
def read_and_process_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
    except UnicodeDecodeError:
        with open(file_path, 'r', encoding='latin-1') as file:
            content = file.read()
    
    content = content.replace('\n', ' ').replace('\r', ' ')
    content = re.sub(r'[^a-zA-Z\s]', ' ', content)
    content = content.lower()
    content = ' '.join(content.split())
    
    return content

def build_directed_graph(text):
    words = text.split()
    word_count = Counter(words)
    graph = nx.DiGraph()

    for i in range(len(words) - 1):
        current_word = words[i]
        next_word = words[i + 1]
        if graph.has_edge(current_word, next_word):
            graph[current_word][next_word]['weight'] += 1
        else:
            graph.add_edge(current_word, next_word, weight=1)
    
    return graph, word_count

def show_directed_graph(graph,highlighted_path=None, save_path=None):
    pos = nx.spring_layout(graph)
    plt.figure(figsize=(12, 8))
    
    
    nx.draw(graph, pos, with_labels=True, node_color='lightblue', edge_color='gray', node_size=3000, font_size=12, font_weight='bold', arrowsize=20)
    
    if highlighted_path:
        edges = [(highlighted_path[i], highlighted_path[i + 1]) for i in range(len(highlighted_path) - 1)]
        nx.draw_networkx_edges(graph, pos, edgelist=edges, edge_color='red', width=2)
        nx.draw_networkx_nodes(graph, pos, nodelist=[highlighted_path[0]], node_color='yellow',node_size=3000)
        nx.draw_networkx_nodes(graph, pos, nodelist=highlighted_path[1:-1], node_color='red')
        nx.draw_networkx_nodes(graph, pos, nodelist=[highlighted_path[-1]], node_color='green',node_size=3000)
        

    edge_labels = nx.get_edge_attributes(graph, 'weight')
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels)

    if save_path:
        plt.savefig(save_path)
    plt.show()


def find_bridge_words(graph, word1, word2):
    if word1 not in graph or word2 not in graph:
        return None
    
    bridge_words = []
    for neighbor in graph.neighbors(word1):
        if graph.has_edge(neighbor, word2):
            bridge_words.append(neighbor)
    
    return bridge_words

'''def print_bridge_words(graph, word1, word2):
    bridge_words = find_bridge_words(graph, word1, word2)
    
    if bridge_words is None:
        return f"No {word1} or {word2} in the graph!"
    elif not bridge_words:
        return f"No bridge words from {word1} to {word2}!"
    elif len(bridge_words) == 1:
        return f"The bridge word from {word1} to {word2} is: {bridge_words[0]}"
    else:
        return f"The bridge words from {word1} to {word2} are: {', '.join(bridge_words)}"
    '''
def print_bridge_words(graph, word1, word2):
    bridge_words = find_bridge_words(graph, word1, word2)
    
    if bridge_words is None:
        return f"No {word1} or {word2} in the graph!"
    elif not bridge_words:
        return f"No bridge words from {word1} to {word2}!"
    elif len(bridge_words) == 1:
        return f"The bridge word from {word1} to {word2} is: {bridge_words[0]}"
    else:
        return f"The bridge words from {word1} to {word2} are: {', '.join(bridge_words)}"

def generate_new_text(input_text, graph):
    # 处理输入文本
    input_text = re.sub(r'[^a-zA-Z\s]', ' ', input_text).lower()
    input_words = input_text.split()
    
    if len(input_words) < 2:
        return input_text  # 如果输入文本不足两个单词，直接返回
    
    new_text = []
    for i in range(len(input_words) - 1):
        word1 = input_words[i]
        word2 = input_words[i + 1]
        
        bridge_words = find_bridge_words(graph, word1, word2)
        new_text.append(word1)
        
        if bridge_words:
            bridge_word = random.choice(bridge_words)
            new_text.append(bridge_word)
    
    new_text.append(input_words[-1])  # 添加最后一个单词
    return ' '.join(new_text)

def calc_shortest_paths(graph, word1, word2=None): #第二个输入可以为空
    if word2:
        if word1 not in graph or word2 not in graph:
            return f"No {word1} or {word2} in the graph!", []
        
        try:
            paths = list(nx.all_shortest_paths(graph, source=word1, target=word2, weight='weight'))
            if not paths:
                return f"No path from {word1} to {word2}!", []
            return "", paths
        except nx.NetworkXNoPath:
            return f"No path from {word1} to {word2}!", []
    else:
        if word1 not in graph:
            return f"No {word1} in the graph!", []
        
        all_paths = {}
        for target in graph.nodes:
            if target != word1:
                try:
                    path = nx.shortest_path(graph, source=word1, target=target, weight='weight')
                    all_paths[target] = path
                except nx.NetworkXNoPath:
                    continue
        return "", all_paths
    
'''def print_shortest_path(graph, word1, word2=None):
    message, paths = calc_shortest_paths(graph, word1, word2)
    if message:
        return message, None
    
    path_lengths = []
    if word2:
        for i, path in enumerate(paths):
            path_length = sum(graph[path[j]][path[j + 1]]['weight'] for j in range(len(path) - 1))
            path_lengths.append((path, path_length))
        return "", path_lengths
    else:
        for target, path in paths.items():
            path_length = sum(graph[path[i]][path[i + 1]]['weight'] for i in range(len(path) - 1))
            path_lengths.append((path, path_length))
        return "", path_lengths

'''
def print_shortest_path(graph, word1, word2=None):
    message, paths = calc_shortest_paths(graph, word1, word2)
    if message:
        return message, None

    path_lengths = []
    if word2:
        for path in paths:
            path_length = sum(graph[path[i]][path[i + 1]]['weight'] for i in range(len(path) - 1))
            path_lengths.append((path, path_length))
        return "", path_lengths
    else:
        for target, path in paths.items():
            path_length = sum(graph[path[i]][path[i + 1]]['weight'] for i in range(len(path) - 1))
            path_lengths.append((path, path_length))
        return "", path_lengths




class GraphApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.graph = None
        self.word_count = None
        self.walk_thread = None
        #self.current_node = random.choice(list(self.graph.nodes))
        #self.next_node = None
        #self.count=0
        #self.path = [self.current_node]
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Text Processing and Graph Visualization")
        
        layout = QtWidgets.QVBoxLayout()
        
        self.openButton = QtWidgets.QPushButton("Open File")
        self.openButton.clicked.connect(self.open_file)
        layout.addWidget(self.openButton)
        
        formLayout = QtWidgets.QFormLayout()
        self.word1Edit = QtWidgets.QLineEdit()
        self.word2Edit = QtWidgets.QLineEdit()
        formLayout.addRow("Word 1:", self.word1Edit)
        formLayout.addRow("Word 2:", self.word2Edit)
        layout.addLayout(formLayout)
        
        self.findButton = QtWidgets.QPushButton("Find Bridge Words")
        self.findButton.clicked.connect(self.find_bridge_words)
        layout.addWidget(self.findButton)
        
        self.resultLabel = QtWidgets.QLabel("")
        layout.addWidget(self.resultLabel)

        self.newTextInput = QtWidgets.QLineEdit()
        layout.addWidget(self.newTextInput)
        
        self.generateButton = QtWidgets.QPushButton("Generate New Text")
        self.generateButton.clicked.connect(self.generate_new_text)
        layout.addWidget(self.generateButton)
        
        self.newTextLabel = QtWidgets.QLabel("")
        layout.addWidget(self.newTextLabel)

        self.shortestPathButton = QtWidgets.QPushButton("Find Shortest Path")
        self.shortestPathButton.clicked.connect(self.find_shortest_path)
        layout.addWidget(self.shortestPathButton)
        
        self.shortestPathLabel = QtWidgets.QLabel("")
        layout.addWidget(self.shortestPathLabel)
        
        self.randomWalkButton = QtWidgets.QPushButton("Random Walk")
        self.randomWalkButton.clicked.connect(self.start_random_walk)
        layout.addWidget(self.randomWalkButton)

        
        
       
       

        


        self.setLayout(layout)
        
    def open_file(self):
        options = QtWidgets.QFileDialog.Options()
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open Text File", "", "Text Files (*.txt);;All Files (*)", options=options)
        if file_path:
            content = read_and_process_file(file_path)
            self.graph, self.word_count = build_directed_graph(content)
            show_directed_graph(self.graph)
    
    def find_bridge_words(self):
        word1 = self.word1Edit.text().strip().lower()
        word2 = self.word2Edit.text().strip().lower()
        if self.graph is None:
            self.resultLabel.setText("Please open a file first.")
        else:
            result = print_bridge_words(self.graph, word1, word2)
            self.resultLabel.setText(result)

        

    def generate_new_text(self):
        input_text = self.newTextInput.text().strip()
        if self.graph is None:
            self.newTextLabel.setText("Please open a file first.")
        else:
            new_text = generate_new_text(input_text, self.graph)
            self.newTextLabel.setText(new_text)

    '''def find_shortest_path(self):
        word1 = self.word1Edit.text().strip().lower()
        word2 = self.word2Edit.text().strip().lower()
        if self.graph is None:
            self.shortestPathLabel.setText("Please open a file first.")
        else:
            message, path_lengths = print_shortest_path(self.graph, word1, word2)
            if message:
                self.shortestPathLabel.setText(message)
            else:
                if word2:
                    path, length = path_lengths[0]
                    self.shortestPathLabel.setText(f"Shortest path from {word1} to {word2}: {' -> '.join(path)}, length: {length}")
                    show_directed_graph(self.graph, highlighted_path=path)
                else:
                    paths_info = []
                    for path, length in path_lengths:
                        paths_info.append(f"{' -> '.join(path)}, length: {length}")
                    self.shortestPathLabel.setText("Shortest paths:\n" + "\n".join(paths_info))
                    if path_lengths:
                        show_directed_graph(self.graph, highlighted_path=path_lengths[0][0])
    '''
    def find_shortest_path(self):
        word1 = self.word1Edit.text().strip().lower()
        word2 = self.word2Edit.text().strip().lower()
        if self.graph is None:
            self.shortestPathLabel.setText("Please open a file first.")
        else:
            message, path_lengths = print_shortest_path(self.graph, word1, word2)
            if message:
                self.shortestPathLabel.setText(message)
            else:
                if word2:
                    paths_info = []
                    for path, length in path_lengths:
                        paths_info.append(f"Shortest path from {word1} to {word2}: {' -> '.join(path)}, length: {length}")
                    self.shortestPathLabel.setText("\n".join(paths_info))
                    
                    # Highlight the first shortest path in the visualization
                    if path_lengths:
                        show_directed_graph(self.graph, highlighted_path=path_lengths[0][0])
                else:
                    paths_info = []
                    for path, length in path_lengths:
                        paths_info.append(f"{' -> '.join(path)}, length: {length}")
                    self.shortestPathLabel.setText("Shortest paths:\n" + "\n".join(paths_info))
                    
                    # Highlight the first shortest path in the visualization
                    if path_lengths:
                        show_directed_graph(self.graph, highlighted_path=path_lengths[0][0])
    '''def start_random_walk(self):
        if self.graph is None:
            QtWidgets.QMessageBox.warning(self, "Warning", "Please open a file first.")
            return
        
        
        
        start_node = random.choice(list(self.graph.nodes))
        current_node = start_node
        path = [current_node]
        visited_edges = set()

        while True:
            out_edges = list(self.graph.out_edges(current_node))
            if not out_edges:
                break

            next_edge = random.choice(out_edges)
            path.append(next_edge[1])
            
            if next_edge in visited_edges:
                break
            
            visited_edges.add(next_edge)
            current_node = next_edge[1]

        show_directed_graph(self.graph, highlighted_path=path)'''
    
    
    def start_random_walk(self):
        
        global count,current_node,path_random
        
        if self.graph is None:
            QtWidgets.QMessageBox.warning(self, "Warning", "Please open a file first.")
            return
        
        
        if(count==0):
            current_node= random.choice(list(self.graph.nodes))
            path_random.append(current_node)
            count=1

        # 定义一个成员变量用于存储当前节点
        #if not hasattr(self, "current_node"):
        #    self.current_node = random.choice(list(self.graph.nodes))

        # 获取当前节点的所有出边
        
        out_edges = list(self.graph.out_edges(current_node))

        # 如果当前节点没有出边，则无法继续游走
        if not out_edges:
            return

        # 从当前节点的出边中随机选择一条边
        next_edge = random.choice(out_edges)

        if next_edge in path_random:
            return

        # 将该边的目标节点设置为当前节点
        next_node = next_edge[1]

        # 构建路径，包括当前节点和目标节点
        path_random.append(next_node) 
        current_node=next_node

        # 显示构建的有向图，并将路径高亮显示
        show_directed_graph(self.graph, highlighted_path=path_random)
   
      
    
  
   

def main():
    
    app = QtWidgets.QApplication([])
    window = GraphApp()
    window.show()
    app.exec_()

if __name__ == "__main__":
    main()
