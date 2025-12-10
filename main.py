import math
import tkinter as tk


def vec_sub(v1, v2):
    return (v1[0] - v2[0], v1[1] - v2[1], v1[2] - v2[2])


def vec_dot(v1, v2):
    return v1[0] * v2[0] + v1[1] * v2[1] + v1[2] * v2[2]


def vec_cross(a, b):
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def vec_len(v):
    return math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2])


def vec_norm(v):
    l = vec_len(v)
    return (v[0] / l, v[1] / l, v[2] / l) if l > 0 else (0, 0, 0)


def carregar_malha(path):
    with open(path, "r", encoding="utf-8") as f:
        lines = [l.strip() for l in f if l.strip() and not l.strip().startswith("#")]

    # número de vértices e triângulos
    vertices_n, triangles_n = map(int, lines[0].split())
    vertices = []
    idx = 1

    # vértices
    for _ in range(vertices_n):
        x, y, z = map(float, lines[idx].split())
        vertices.append((x, y, z))
        idx += 1

    # triângulos
    triangles = []
    for _ in range(triangles_n):
        vertex_1, vertex_2, vertex_3 = map(int, lines[idx].split())
        # Converte para 0-based (Python usa índices começando de 0)
        triangles.append((vertex_1 - 1, vertex_2 - 1, vertex_3 - 1))
        idx += 1

    return vertices, triangles


def carregar_camera(path):
    data = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = [s.strip() for s in line.split("=", 1)]
            vals = v.split()
            if len(vals) > 1:
                data[k] = tuple(map(float, vals))
            else:
                data[k] = float(vals[0])
    return data


def normalizar(v):
    x, y, z = v
    n = math.sqrt(x * x + y * y + z * z)
    if n == 0:
        return (0.0, 0.0, 0.0)
    return (x / n, y / n, z / n)


def produto_vetorial(vetor_1, vetor_2):
    return (
        vetor_1[1] * vetor_2[2] - vetor_1[2] * vetor_2[1],
        vetor_1[2] * vetor_2[0] - vetor_1[0] * vetor_2[2],
        vetor_1[0] * vetor_2[1] - vetor_1[1] * vetor_2[0],
    )


def produto_escalar(vetor_1, vetor_2):
    return vetor_1[0] * vetor_2[0] + vetor_1[1] * vetor_2[1] + vetor_1[2] * vetor_2[2]


def base_coordenadas_camera(N, V):
    v_normalizado = normalizar(V)
    n_normalizado = normalizar(N)
    U = normalizar(produto_vetorial(v_normalizado, n_normalizado))
    V_corrigido = produto_vetorial(n_normalizado, U)
    return (U, V_corrigido, n_normalizado)


def converter_global_para_camera(ponto, base_camera, posicao_camera):
    ponto_transladado = (
        ponto[0] - posicao_camera[0],
        ponto[1] - posicao_camera[1],
        ponto[2] - posicao_camera[2],
    )
    return (
        produto_escalar(base_camera[0], ponto_transladado),
        produto_escalar(base_camera[1], ponto_transladado),
        produto_escalar(base_camera[2], ponto_transladado),
    )


def projetar_ponto(ponto_camera, d):
    if ponto_camera[2] <= 0:
        return None  # Ponto atrás da câmera
    return (
        (ponto_camera[0] * d) / ponto_camera[2],
        (ponto_camera[1] * d) / ponto_camera[2],
    )


def converter_para_tela(ponto_normalizado, largura, altura):
    return (
        int(((ponto_normalizado[0] + 1) / 2) * (largura - 1)),
        int(((1 - ponto_normalizado[1]) / 2) * (altura - 1)),
    )


def clipar_ponto(x_ndc, y_ndc):
    # Clipping: Garantir que x e y fiquem no intervalo [-1, 1]
    if x_ndc < -1 or x_ndc > 1 or y_ndc < -1 or y_ndc > 1:
        return None  # Ponto fora da tela, não desenha
    return x_ndc, y_ndc


def interpolacao_linear(y, y0, y1, x0, x1):
    if y1 == y0:
        return x0  # Evita divisão por zero, retorna x0
    return x0 + ((x1 - x0) * (y - y0)) / (y1 - y0)


def scan_line_fill(triangulos, vertices_projetados, params, z_buffer_matrix):
    # Índices: 0=sx, 1=sy, 2=z, 3-5=N, 6-8=PosMundo

    for tri in triangulos:
        v0 = vertices_projetados[tri[0]]
        v1 = vertices_projetados[tri[1]]
        v2 = vertices_projetados[tri[2]]

        if v0 is None or v1 is None or v2 is None:
            continue

        # Ordena por Y
        V0, V1, V2 = sorted([v0, v1, v2], key=lambda v: v[1])

        # define sub-triangulos
        if V0[1] != V1[1] and V1[1] != V2[1]:
            # interpolar para o vértice de corte (Vm)
            y_split = V1[1]

            def interp_full(va, vb, y):
                res = []
                for i in range(9):
                    res.append(interpolacao_linear(y, va[1], vb[1], va[i], vb[i]))
                return tuple(res)

            Vm = interp_full(V0, V2, y_split)
            sub_triangles = [[V0, V1, Vm], [V1, Vm, V2]]
        else:
            sub_triangles = [[V0, V1, V2]]

        for t in sub_triangles:
            t = sorted(t, key=lambda v: v[1])
            VA, VB, VC = t[0], t[1], t[2]

            y_start, y_end = int(VA[1]), int(VC[1])
            if VB[1] == VC[1]:  # base plana
                left, right = (VA, VB), (VA, VC)
            else:  # topo plano
                left, right = (VA, VC), (VB, VC)

            for y in range(y_start, y_end + 1):
                if y < 0 or y >= H:
                    continue

                # interpola inicio e fim da linha (scanline)
                def get_val(idx, y_curr, start_v, end_v):
                    return interpolacao_linear(
                        y_curr, start_v[1], end_v[1], start_v[idx], end_v[idx]
                    )

                # calcula X (idx 0)
                xa = get_val(0, y, left[0], left[1])
                xb = get_val(0, y, right[0], right[1])

                # garante ordem
                if xa > xb:
                    xa, xb = xb, xa
                    left, right = (
                        right,
                        left,
                    )

                x_start, x_end = int(xa), int(xb)

                for x in range(x_start, x_end + 1):
                    if x < 0 or x >= W:
                        continue

                    # interpola Z (idx 2)
                    za = get_val(2, y, left[0], left[1])
                    zb = get_val(2, y, right[0], right[1])
                    z_pixel = interpolacao_linear(x, xa, xb, za, zb)

                    if z_pixel < z_buffer_matrix[x][y]:
                        z_buffer_matrix[x][y] = z_pixel

                        # interpola Normal (3,4,5) e PosMundo (6,7,8)

                        def interp_vec(idx_start):
                            v_a = [
                                get_val(i, y, left[0], left[1])
                                for i in range(idx_start, idx_start + 3)
                            ]
                            v_b = [
                                get_val(i, y, right[0], right[1])
                                for i in range(idx_start, idx_start + 3)
                            ]
                            return tuple(
                                interpolacao_linear(x, xa, xb, v_a[i], v_b[i])
                                for i in range(3)
                            )

                        N_pixel = interp_vec(3)
                        P_pixel = interp_vec(6)

                        # calcula cor e pinta
                        cor = calcular_phong(P_pixel, N_pixel, params)
                        set_pixel(x, y, cor)


def render_points(parametros_camera, vertices, triangulos):
    # limpa Z-Buffer
    global z_buffer
    z_buffer = [[float("inf")] * H for _ in range(W)]

    normais = calcular_normais_vertices(vertices, triangulos)
    base = base_coordenadas_camera(parametros_camera["N"], parametros_camera["V"])

    vertices_processados = []

    for i, v in enumerate(vertices):
        ponto_camera = converter_global_para_camera(v, base, parametros_camera["C"])
        ponto_projetado = projetar_ponto(ponto_camera, parametros_camera["d"])
        if ponto_projetado is None:
            continue
        ponto_normalizado = (
            ponto_projetado[0] / parametros_camera["hx"],
            ponto_projetado[1] / parametros_camera["hy"],
        )
        ponto_normalizado = clipar_ponto(ponto_normalizado[0], ponto_normalizado[1])
        if ponto_normalizado is None:
            continue
        tela = converter_para_tela(ponto_normalizado, W, H)

        # (ScreenX, ScreenY, ProfundidadeZ, NormalX, NormalY, NormalZ, WorldX, WorldY, WorldZ)
        dados_vertice = (
            tela[0],
            tela[1],
            ponto_camera[2],
            normais[i][0],
            normais[i][1],
            normais[i][2],
            v[0],
            v[1],
            v[2],
        )
        vertices_processados.append(dados_vertice)

    scan_line_fill(triangulos, vertices_processados, parametros_camera, z_buffer)


def calcular_normais_vertices(vertices, triangulos):
    normais = [(0.0, 0.0, 0.0)] * len(vertices)
    for tri in triangulos:
        v0, v1, v2 = vertices[tri[0]], vertices[tri[1]], vertices[tri[2]]
        # Normal da face
        edge1 = vec_sub(v1, v0)
        edge2 = vec_sub(v2, v0)
        nf = vec_cross(edge1, edge2)
        # Acumula nos vértices
        for i in tri:
            normais[i] = (
                normais[i][0] + nf[0],
                normais[i][1] + nf[1],
                normais[i][2] + nf[2],
            )
    return [vec_norm(n) for n in normais]


def calcular_phong(P_mundo, N_mundo, params):
    L = vec_norm(vec_sub(params["Pl"], P_mundo))  # vetor Luz
    V = vec_norm(vec_sub(params["C"], P_mundo))  # vetor Visão
    N = vec_norm(N_mundo)

    # Ambiente
    Iamb, Ka = params["Iamb"], params["Ka"]
    cor = [Iamb[0] * Ka, Iamb[1] * Ka, Iamb[2] * Ka]

    N_dot_L = vec_dot(N, L)
    if N_dot_L > 0:
        # difusa
        Il, Kd, Od = params["Il"], params["Kd"], params["Od"]
        for i in range(3):
            cor[i] += Il[i] * Kd[i] * Od[i] * N_dot_L

        # especular
        R = vec_sub(tuple(2 * N_dot_L * n for n in N), L)  # R = 2N(N.L) - L
        R_dot_V = vec_dot(R, V)
        if R_dot_V > 0:
            Ks, eta = params["Ks"], params["eta"]
            spec = Ks * (R_dot_V**eta)
            for i in range(3):
                cor[i] += Il[i] * spec

    return (min(255, int(cor[0])), min(255, int(cor[1])), min(255, int(cor[2])))


def set_pixel(x: int, y: int, rgb: tuple[int, int, int]):
    if 0 <= x < W and 0 <= y < H:
        r, g, b = rgb
        img.put(f"#{r:02x}{g:02x}{b:02x}", to=(x, y))


def refresh_screen():
    global img, lbl
    img = tk.PhotoImage(width=W, height=H)
    img.put("#000000", to=(0, 0, W, H))
    lbl.config(image=img)
    lbl.image = img
    try:
        vertices, triangulos = carregar_malha(malha_file)
        parametros_camera = carregar_camera(camera_file)
        render_points(parametros_camera, vertices, triangulos)
        print("Render concluído.")
    except Exception as e:
        print(f"Erro: {e}")


malha_file = "objetos/calice2.byu"
camera_file = "camera.txt"
W, H = 800, 800
z_buffer = []

root = tk.Tk()
root.title("2VA - Phong e Z-Buffer")
img = tk.PhotoImage(width=W, height=H)
lbl = tk.Label(root, image=img)
lbl.pack()

root.after(100, refresh_screen)

root.bind("<Escape>", lambda e: root.destroy())
root.bind("<r>", lambda e: refresh_screen())  # 'r' to reload/redraw
root.mainloop()
