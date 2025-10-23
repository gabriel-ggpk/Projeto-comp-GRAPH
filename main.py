import math
import tkinter as tk


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
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            k, v = [s.strip() for s in line.split("=", 1)]
            if k in ("N", "V", "C"):
                vals = list(map(float, v.split()))
                if len(vals) != 3:
                    raise ValueError(f"Parâmetro {k} inválido: '{v}'")
                data[k] = tuple(vals)
            elif k in ("d", "hx", "hy"):
                data[k] = float(v)

    for key in ("N", "V", "C", "d", "hx", "hy"):
        if key not in data:
            raise ValueError(f"Parâmetro de câmera ausente: {key}")
    return data


def normalizar(v):
    x, y, z = v
    n = math.sqrt(x * x + y * y + z * z)
    if n == 0:
        if z is None:
            return (0.0, 0.0)
        return (0.0, 0.0, 0.0)
    if z is None:
        return (x / n, y / n)
    return (x / n, y / n, z / n)


def produto_vetorial(vetor_1, vetor_2):
    return (
        vetor_1[1] * vetor_2[2] - vetor_1[2] * vetor_2[1],
        vetor_1[2] * vetor_2[0] - vetor_1[0] * vetor_2[2],
        vetor_1[0] * vetor_2[1] - vetor_1[1] * vetor_2[0],
    )


def produto_escalar(vetor_1, vetor_2):
    result = vetor_1[0] * vetor_2[0] + vetor_1[1] * vetor_2[1] + vetor_1[2] * vetor_2[2]
    return result


def base_coordenadas_camera(N, V):
    v_normalizado = normalizar(V)
    n_normalizado = normalizar(N)
    resultado = (
        normalizar(produto_vetorial(v_normalizado, n_normalizado)),
        v_normalizado,
        n_normalizado,
    )
    print(f"Base da câmera: {resultado}")
    return resultado


def converter_global_para_camera(ponto, base_camera, posicao_camera):
    ponto_transladado = (
        ponto[0] - posicao_camera[0],
        ponto[1] - posicao_camera[1],
        ponto[2] - posicao_camera[2],
    )
    ponto_camera = (
        produto_escalar(base_camera[0], ponto_transladado),
        produto_escalar(base_camera[1], ponto_transladado),
        produto_escalar(base_camera[2], ponto_transladado),
    )
    return ponto_camera


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


def scan_line_fill(triangulos, vertices):
    pixels = set()

    for tri in triangulos:
        v0 = vertices[tri[0]]
        v1 = vertices[tri[1]]
        v2 = vertices[tri[2]]

        # ordena por Y crescente
        V0, V1, V2 = sorted([v0, v1, v2], key=lambda v: v[1])

        if V0[1] != V1[1] and V1[1] != V2[1]:
            y_split = V1[1]
            x_split = interpolacao_linear(y_split, V0[1], V2[1], V0[0], V2[0])
            Vm = [x_split, y_split]

            # divide em dois sub-triângulos
            # base plana
            top_triangle = [V0, V1, Vm]
            # topo plano
            bottom_triangle = [V1, Vm, V2]

            sub_triangles = [top_triangle, bottom_triangle]
        else:
            sub_triangles = [[V0, V1, V2]]

        for t in sub_triangles:
            # ordena vértices por Y
            t = sorted(t, key=lambda v: v[1])
            V0, V1, V2 = t

            y_start = int(V0[1])
            y_end = int(V2[1])

            if V1[1] == V2[1]:
                # base plana
                left_start, left_end = V0, V1
                right_start, right_end = V0, V2
            else:
                # topo plano
                left_start, left_end = V0, V2
                right_start, right_end = V1, V2

            # percorre cada linha horizontal
            for y in range(y_start, y_end + 1):
                # calcula X na aresta esquerda e direita
                x_left = interpolacao_linear(
                    y, left_start[1], left_end[1], left_start[0], left_end[0]
                )
                x_right = interpolacao_linear(
                    y, right_start[1], right_end[1], right_start[0], right_end[0]
                )

                # garante ordem correta
                if x_left > x_right:
                    x_left, x_right = x_right, x_left

                # preenche pixels da linha
                for x in range(int(x_left), int(x_right) + 1):
                    pixels.add((x, y))

    return pixels


def render_points(parametros_camera, vertices, triangulos):
    base = base_coordenadas_camera(parametros_camera["N"], parametros_camera["V"])
    pontos_tela = []
    for v in vertices:
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
        ponto_tela = converter_para_tela(ponto_normalizado, W, H)
        pontos_tela.append(ponto_tela)
    pixels = scan_line_fill(triangulos, pontos_tela)
    print(f"Pixels preenchidos: {len(pixels)}")
    for p in pixels:
        set_pixel(p[0], p[1], (255, 255, 255))
    return pontos_tela


def set_pixel(x: int, y: int, rgb: tuple[int, int, int]):
    """Desenha UM pixel (x,y) na cor (r,g,b)."""
    if 0 <= x < W and 0 <= y < H:
        r, g, b = rgb
        img.put(f"#{r:02x}{g:02x}{b:02x}", to=(x, y))


def refresh_screen():
    global img, lbl
    new_img = tk.PhotoImage(width=W, height=H)
    img = new_img
    lbl.config(image=img)
    lbl.image = img
    vertices, triangulos = carregar_malha(malha_file)
    parametros_camera = carregar_camera(camera_file)
    render_points(parametros_camera, vertices, triangulos)


# arquivos de definição
malha_file = "objetos/vaso.byu"
camera_file = "camera.txt"
W, H = 800, 800

# Carrega a malha e a câmera
try:
    vertices, triangulos = carregar_malha(malha_file)
    print(f"Vértices: {len(vertices)}")
    print(f"Triângulos: {len(triangulos)}")
except Exception as e:
    print(f"Erro ao carregar malha: {e}")

try:
    parametros_camera = carregar_camera(camera_file)
    print(f"Parâmetros da Câmera: {parametros_camera}")
except Exception as e:
    print(f"Erro ao carregar câmera: {e}")
root = tk.Tk()
root.title("Só pixel :)  (stdlib)")
img = tk.PhotoImage(width=W, height=H)
lbl = tk.Label(root, image=img)
lbl.pack()

pontos_tela = render_points(parametros_camera, vertices, triangulos)
root.bind("<Escape>", lambda e: root.destroy())
root.bind("<r>", lambda e: refresh_screen())  # 'r' to reload/redraw
root.mainloop()
