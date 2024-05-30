import re
from collections import Counter
import networkx as nx
import matplotlib.pyplot as plt
import random

def read_and_process_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
    except UnicodeDecodeError:
        with open(file_path, 'r', encoding='latin-1') as file:
            content = file.read()
    
    # 将换行符和回车符替换为空格
    content = content.replace('\n', ' ').replace('\r', ' ')
    
    # 将非字母字符替换为空格
    content = re.sub(r'[^a-zA-Z\s]', ' ', content)
    
    # 将所有字符转换为小写
    content = content.lower()
    
    # 移除多余的空格
    content = ' '.join(content.split())
    
    return content

def build_directed_graph(text):
    words = text.split()  # 按空格分割成单词列表
    word_count = Counter(words)  # 统计每个单词出现的次数

    # 初始化有向图
    graph = nx.DiGraph()

    # 添加节点和边
    for i in range(len(words) - 1):
        current_word = words[i]
        next_word = words[i + 1]
        if graph.has_edge(current_word, next_word):
            graph[current_word][next_word]['weight'] += 1
        else:
            graph.add_edge(current_word, next_word, weight=1)
    
    return graph, word_count

def show_directed_graph(graph, save_path=None):
    pos = nx.spring_layout(graph)  # 生成节点布局位置
    plt.figure(figsize=(12, 8))  # 设置图形大小
    nx.draw(graph, pos, with_labels=True, node_color='lightblue', edge_color='gray', node_size=3000, font_size=12, font_weight='bold', arrowsize=20)
    
    # 绘制边上的权重
    edge_labels = nx.get_edge_attributes(graph, 'weight')
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels)

    if save_path:
        plt.savefig(save_path)  # 保存图形到文件
    plt.show()  # 展示图形

def find_bridge_words(graph, word1, word2):
    if word1 not in graph or word2 not in graph:
        return None
    
    bridge_words = []
    for neighbor in graph.neighbors(word1):
        if graph.has_edge(neighbor, word2):
            bridge_words.append(neighbor)
    
    return bridge_words

def print_bridge_words(graph, word1, word2):
    bridge_words = find_bridge_words(graph, word1, word2)
    
    if bridge_words is None:
        print(f"No {word1} or {word2} in the graph!")
    elif not bridge_words:
        print(f"No bridge words from {word1} to {word2}!")
    elif len(bridge_words) == 1:
        print(f"The bridge word from {word1} to {word2} is: {bridge_words[0]}")
    else:
        print(f"The bridge words from {word1} to {word2} are: {', '.join(bridge_words)}")

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

def print_shortest_path(graph, word1, word2=None): #打印路径信息
    message, paths = calc_shortest_paths(graph, word1, word2)
    if message:
        print(message)
        return
    
    if word2:
        for i, path in enumerate(paths):
            path_length = sum(graph[path[j]][path[j + 1]]['weight'] for j in range(len(path) - 1))
            print(f"Path {i + 1} from {word1} to {word2}: {' -> '.join(path)}, length: {path_length}")
    else:
        for target, path in paths.items():
            path_length = sum(graph[path[i]][path[i + 1]]['weight'] for i in range(len(path) - 1))
            print(f"Shortest path from {word1} to {target}: {' -> '.join(path)}, length: {path_length}")

def random_walk(graph, start_node):
    if start_node not in graph:
        return f"No {start_node} in the graph!", []

    current_node = start_node
    path = [current_node]
    visited_edges = set()

    while True:
        out_edges = list(graph.out_edges(current_node))
        if not out_edges:  # 当前节点没有出边，结束
            break

        next_edge = random.choice(out_edges)  # 随机选择一条出边
        path.append(next_edge[1])  # 记录边的终点
        
        if next_edge in visited_edges:  # 如果边已经被访问过，结束
            break
        
        visited_edges.add(next_edge)
        current_node = next_edge[1]

    return "", path

def perform_random_walks(graph, start_node, num_walks=5, output_file='random_walks.txt'):
    with open(output_file, 'w', encoding='utf-8') as file:
        for i in range(num_walks):
            message, path = random_walk(graph, start_node)
            if message:
                print(message)
                file.write(message + '\n')
                continue

            walk_result = ' -> '.join(path)
            print(f"Random walk {i + 1}: {walk_result}")
            file.write(f"Random walk {i + 1}: {walk_result}\n")


# 示例用法：
file_path = 'C:\\Users\\fcy\\Desktop\\software lab1\\test_text.txt'
processed_text = read_and_process_file(file_path)
graph, word_count = build_directed_graph(processed_text)

# 打印单词出现次数统计
print("单词出现次数统计:")
for word, count in word_count.items():
    print(f"{word}: {count}")

# 打印有向图的边和权重
print("\n有向图边和权重:")
for edge in graph.edges(data=True):
    print(f"{edge[0]} -> {edge[1]}, 权重: {edge[2]['weight']}")

# 展示并保存有向图
show_directed_graph(graph, save_path='directed_graph.png')

# 示例查询桥接词
word1 = 'seek'
word2 = 'explore'
print_bridge_words(graph, word1, word2)

# 查询桥接词并生成新文本
input_text = "Seek to explore new and exciting synergies"
new_text = generate_new_text(input_text, graph)
print(f"输入文本: {input_text}")
print(f"生成文本: {new_text}")

# 示例计算最短路径
print_shortest_path(graph, 'to', '')
print_shortest_path(graph, 'to', 'and')

# 执行随机游走并输出结果
start_node = "to"  # 示例起始节点
perform_random_walks(graph, start_node)



