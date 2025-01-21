import sys
import os
import math

import subprocess
result = subprocess.run(["pip", "show", "pillow"], capture_output=True, encoding="utf-8")
if result.returncode != 0:
    print(f"\033[91m{result.stderr}\033[0m")
    exit()

from PIL import Image

image_path:str|None = None
square_size:int = 0
start_x:int = 0
start_y:int = 0


def main():
    if image_path is None:
        convert_all_images()
    else:
        convert_image(image_path)
    print("--------[ COMPLETE ]--------")


def convert_all_images():
    for fn in os.listdir(os.curdir):
        if fn.lower().endswith(".jpg") or fn.lower().endswith(".png"):
            convert_image(fn, True)


def convert_image(img_path, in_one_file:bool=False):
    if not os.path.exists(img_path):
        print(f"Image \"{img_path}\" not found!")
        return
    img = Image.open(img_path, "r").convert("L")
    if not in_one_file:
        txt_path = img_path[:img_path.rfind(".")]
        mode = "w"
    else:
        txt_path = "result"
        mode = "a+"
    with open(f"{txt_path}.txt", mode, encoding="utf-8") as txt:
        if square_size == 0:
            auto_detect_size_and_offset(img)
        for y in range(9):
            for x in range(9):
                px = start_x + square_size * x
                py = start_y + square_size * y
                pw = px + square_size
                ph = py + square_size
                piece = img.crop((px, py, pw, ph))
                num = recognize(piece)
                if num:
                    txt.write(f"{x}{y}{num}")
        txt.write("\n")
    img.close()


def recognize(p:Image.Image):
    maxv = 0
    minv = 255
    for y in range(square_size):
        for x in range(square_size):
            v = p.getpixel([x, y])
            if v > maxv:
                maxv = v
            if v < minv:
                minv = v
    border = int((maxv - minv) * 0.3)
    ba = []
    for y in range(square_size):
        h_solid_length = 0
        for x in range(square_size):
            v = p.getpixel([x, y])
            if minv <= v < minv + border:
                ba.append(1)
                h_solid_length += 1
            else:
                ba.append(0)
        if h_solid_length > int(square_size * 0.6):
            for i in range(square_size):
                ba[y * square_size + i] = 0
                if y > 0:
                    if ba[(y - 1) * square_size + i] == 1:
                        ba[y * square_size + i] = 1
    for x in range(square_size):
        v_solid_length = 0
        for y in range(square_size):
            if ba[y * square_size + x] == 1:
                v_solid_length += 1
        if v_solid_length > int(square_size * 0.8):
            for i in range(square_size):
                ba[i * square_size + x] = 0
    num = 0
    if ba.count(1) > int(len(ba) * 0.01):
        return recognize_number(ba)
    return num

def recognize_number(arr):
    top = 0
    bottom = square_size - 1
    left = 0
    right = square_size - 1
    for i in range(square_size):
        h_zeros_top = arr[i * square_size : (i + 1) * square_size].count(0)
        if h_zeros_top != square_size and top == 0:
            top = i
        h_zeros_bottom = arr[(square_size - i - 1) * square_size : (square_size - i) * square_size].count(0)
        if h_zeros_bottom != square_size and bottom == square_size - 1:
            bottom = square_size - i - 1
        v_zeros_left = 0
        v_zeros_right = 0
        for j in range(square_size):
            if arr[j * square_size + i] == 0:
                v_zeros_left += 1
            if arr[j * square_size + (square_size - i - 1)] == 0:
                v_zeros_right += 1
        if v_zeros_left != square_size and left == 0:
            left = i
        if v_zeros_right != square_size and right == square_size - 1:
            right = square_size - i - 1
        if top != 0 and  bottom != square_size - 1 and left != 0 and right != square_size - 1:
            break
    # START RECOGNIZE NUMBER
    nw = right - left + 1
    nh = bottom - top + 1
    # 1  without stroke in bottom
    if nw / nh < 0.4:
        return 1
    # other numbers
    p = int(math.floor(nh * 0.1))
    gh = math.ceil(nh / p) * p
    gw = math.ceil(nw / p) * p
    zp = set()
    for y in range(0, gh, p):
        for x in range(0, gw, p):
            px = []
            for i in range(p * p):
                px.append( arr[(top + y + i // p) * square_size + left + x + i % p] )
            f = px.count(1) / len(px)
            if f > 0.475:
                zp.add((x // p, y // p))
    # 0 1 2 3 4 5 6 7 8 9
    vc = get_lines(gh // p, gw // p // 2, True, zp)
    if len(vc) == 2:
        hc = get_lines(gw // p, vc[0]["start"][1], False, zp)
        if vc[0]["start"][1] == 0 and len(hc) == 1 and hc[0]["count"] / (gw // p) > 0.3:
            if vc[1]["finish"][1] >= gh // p - 2:
                return 0 # hollow zero
            if vc[1]["count"] >= 1 and hc[0]["count"] / (gw // p) > 0.775:
                return 7
        else:
            return 4
    elif len(vc) == 3:
        fve_t = get_lines(gw // p, vc[0]["start"][1], False, zp)
        if len(fve_t) == 1 and fve_t[0]["count"] / (gw // p) > 0.775:
            return 5
        two_b = get_lines(gw // p, vc[2]["finish"][1], False, zp)
        if len(two_b) == 1 and two_b[0]["count"] / (gw // p) > 0.775:
            return 2
        ones = []
        for vi in range(vc[len(vc) - 1]["finish"][1] + 1):
            ld = get_lines(gw // p, vi, False, zp)
            if len(ld) == 1:
                if ones:
                    if vi - ones[len(ones) - 1]["line"]["finish"][1] > ones[len(ones) - 1]["vcount"]:
                        ones.append({"line":ld[0], "vcount":1})
                    else:
                        ones[len(ones) - 1]["vcount"] += 1
                else:
                    ones.append({"line":ld[0], "vcount":1})
        if len(ones) == 3 and ones[1]["vcount"] / (gw // p) > 0.3:
            return 3
        if len(ones) == 3 and ones[1]["line"]["count"] / (gw // p) > 0.45:
            return 8
        if len(ones) >= 3:
            mi = 0
            minc = None
            for mo in ones[1:len(ones)-1]:
                if mi == 0:
                    minc = { "count":mo["line"]["count"], "index":mi }
                elif minc["count"] > mo["line"]["count"]:
                    minc["count"] = mo["line"]["count"]
                    minc["index"] = mi
                mi += 1
            if ones[1 + minc["index"]]["line"]["start"][1] < gh // p // 2:
                return 6
            elif ones[1 + minc["index"]]["line"]["start"][1] > gh // p // 2:
                return 9
    pstr = ""
    for my in range(gh // p):
        pstr += "\n"
        for mx in range(gw // p):
            if (mx, my) in zp:
                pstr += "@"
            else:
                pstr += "'"
    print("CAN\'T RECOGNIZE NUMBER!")
    print(pstr)
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    return 0

def get_lines(size:int, c:int, is_v:bool, points:set)->list[dict]:
    vc = []
    for l in range(size):
        v = (c, l) if is_v else (l, c)
        if v in points:
            if vc:
                if l - vc[len(vc) - 1]["finish"][1 if is_v else 0] > 1:
                    vc.append({"start":v, "finish":v, "count":1})
                else:
                    vc[len(vc) - 1]["finish"] = v
                    vc[len(vc) - 1]["count"] += 1
            else:
                vc.append({"start":v, "finish":v, "count":1})
    return vc



def auto_detect_size_and_offset(img:Image.Image):
    global square_size, start_x, start_y
    i = 0
    left = True
    right = True
    top = True
    bottom = True
    colors = {"left":None, "top":None, "right":None, "bottom":None}
    w = img.width
    h = img.height
    lx = 0
    ty = 0
    rx = w - 1
    by = h - 1
    while left or right or top or bottom:
        if left:
            c = img.getpixel([i, h // 2])
            if colors["left"] is None:
                colors["left"] = c
            elif abs(colors["left"] - c) > 30:
                lx = i
                left = False
        if right:
            c = img.getpixel([w - 1 - i, h // 2])
            if colors["right"] is None:
                colors["right"] = c
            elif abs(colors["right"] - c) > 30:
                rx = w - 1 - i
                right = False
        if top:
            c = img.getpixel([w // 2, i])
            if colors["top"] is None:
                colors["top"] = c
            elif abs(colors["top"] - c) > 30:
                ty = i
                top = False
        if bottom:
            c = img.getpixel([w // 2, h - 1 - i])
            if colors["bottom"] is None:
                colors["bottom"] = c
            elif abs(colors["bottom"] - c) > 30:
                by = h - 1 - i
                bottom = False
        i += 1
    start_x = lx
    start_y = ty
    square_size = min((rx - lx + 1) // 9, (by - ty + 1) // 9)



if __name__ == "__main__":
    args = sys.argv[1:]
    if args:
        al = len(args)
        image_path = args[0]
        if al > 1:
            square_size = int(args[1])
        if al > 2:
            start_x = int(args[2])
        if al > 3:
            start_y = int(args[3])
    main()
