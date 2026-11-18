#include <algorithm>
#include <iostream>
#include <queue>
#include <utility>
#include <vector>

// Entrada: numero de vertices, numero de aristas y pares de extremos (base 0).
// Salida: estados reales del algoritmo, uno por linea: accion, vertice, id,
// pila, resultado parcial y aristas consumidas.
void lista(const std::vector<int>& xs) {
    std::cout << xs.size();
    for (int x : xs) std::cout << ' ' << x;
}
int main() {
    int n, m;
    if (!(std::cin >> n >> m) || n <= 0 || m < 0) return 1;
    std::vector<std::vector<std::pair<int,int>>> adj(n);
    for (int id = 0; id < m; ++id) {
        int u, v;
        if (!(std::cin >> u >> v) || u < 0 || v < 0 || u >= n || v >= n) return 1;
        adj[u].push_back({v,id}); adj[v].push_back({u,id});
    }
    for (const auto& a : adj) if (a.size() % 2) return 2;
    int start = 0;
    while (start < n && adj[start].empty()) ++start;
    if (start == n) start = 0;
    std::vector<bool> seen(n, false);
    std::queue<int> q;
    seen[start] = true; q.push(start);
    while (!q.empty()) {
        int v = q.front(); q.pop();
        for (auto edge : adj[v]) if (!seen[edge.first]) {
            seen[edge.first] = true; q.push(edge.first);
        }
    }
    for (int v = 0; v < n; ++v) if (!adj[v].empty() && !seen[v]) return 2;
    std::vector<bool> used(m, false);
    std::vector<int> next(n, 0), stack(1, start), result, used_order;
    auto event = [&](const char* action, int vertex, int edge) {
        std::cout << action << ' ' << vertex << ' ' << edge << ' ';
        lista(stack); std::cout << ' '; lista(result); std::cout << ' ';
        lista(used_order); std::cout << '\n';
    };
    event("start", start, -1);
    while (!stack.empty()) {
        int v = stack.back();
        while (next[v] < static_cast<int>(adj[v].size()) && used[adj[v][next[v]].second]) ++next[v];
        if (next[v] == static_cast<int>(adj[v].size())) {
            result.push_back(v); stack.pop_back(); event("pop", v, -1);
        } else {
            auto edge = adj[v][next[v]++];
            used[edge.second] = true; used_order.push_back(edge.second);
            stack.push_back(edge.first); event("push", edge.first, edge.second);
        }
    }
    if (result.size() != static_cast<std::size_t>(m + 1)) return 3;
}
