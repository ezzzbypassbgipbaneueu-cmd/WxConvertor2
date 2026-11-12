#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Minecraft Java/Bedrock -> Blockman GO Texture Converter.

Uso:
    python mc_to_blockman.py Cryene64x.zip
    python mc_to_blockman.py Cryene64x.zip Cryene64bg.zip

Entrada : SOMENTE o ZIP do Resource Pack (Minecraft Java, ou Bedrock .zip/.mcpack).
Saida   : <nome>_bg.zip (ou o nome informado) + <saida>_relatorio.json

A referencia do Blockman GO (nomes, tamanhos, atlas de itens) vem embutida em
bg_reference/ (distribuida junto com este programa). Nenhum ZIP do Blockman GO
e solicitado em tempo de execucao.

Dependencia unica: Pillow  (pip install pillow)
"""
import argparse
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from collections import OrderedDict
from pathlib import Path

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    sys.exit("Pillow nao encontrado. Instale com: pip install pillow")

import bg_mappings

HERE = Path(__file__).resolve().parent
REF_DIR = HERE / "bg_reference"
OUT_BLOCKS_DIR = "Media/Textures/64pixBlocks/"
OUT_ITEMS_DIR = "Media/Textures/Items/"
NEAREST = Image.NEAREST
IMG_EXTS = (".png", ".tga")

# pack_format -> versoes do Minecraft Java (apenas informativo no relatorio)
PACK_FORMATS = {
    1: "1.6.1-1.8.9", 2: "1.9-1.10.2", 3: "1.11-1.12.2", 4: "1.13-1.14.4",
    5: "1.15-1.16.1", 6: "1.16.2-1.16.5", 7: "1.17.x", 8: "1.18.x",
    9: "1.19-1.19.2", 12: "1.19.3", 13: "1.19.4", 15: "1.20-1.20.1",
    18: "1.20.2", 22: "1.20.3-1.20.4", 32: "1.20.5-1.20.6", 34: "1.21-1.21.1",
}

CATEGORIES_NOT_SUPPORTED = OrderedDict([
    ("entidades_e_mobs", "entity/"),
    ("nuvens_sol_lua_ambiente", "environment/ (clouds, sun, moon_phases)"),
    ("agua_e_lava", "liquidos animados"),
    ("particulas", "particle/"),
    ("interface", "gui/"),
    ("armaduras_no_corpo", "models/armor/"),
    ("animacoes_mcmeta", "*.mcmeta"),
])


# --------------------------------------------------------------- leitura Java
class JavaPack(object):
    """Resource Pack Java lido em memoria (o ZIP original nunca e alterado)."""

    def __init__(self, path):
        self.path = str(path)
        self.zf = None
        self.prefix = ""
        self.members = {}      # "block/stone" -> nome do membro no zip
        self.other = []        # arquivos fora de block/blocks/item/items
        self.pack_meta = {}
        self.dirs = set()
        self.sky = {}          # "cloud1.png" -> membro (mcpatcher|optifine /sky/world0/)
        self.misc = {}         # "enchanted_item_glint" -> membro (textures/misc/*.png)
        self.sounds = {}       # "damage/hit1" -> (membro, extensao)
        self.edition = "java"
        self.warnings = []
        self.manifest = {}

    def close(self):
        if self.zf:
            self.zf.close()

    def has(self, folder, stem):
        return ("%s/%s" % (folder, stem)) in self.members

    def load(self, folder, stem):
        """Abre a imagem como RGBA, ou levanta ValueError/OSError."""
        data = self.zf.read(self.members["%s/%s" % (folder, stem)])
        im = Image.open(io.BytesIO(data))
        im.load()
        return im.convert("RGBA")


def read_java_pack(path):
    """Le o ZIP do Resource Pack e indexa assets/minecraft/textures/."""
    if not zipfile.is_zipfile(path):
        raise ValueError("'%s' nao e um arquivo ZIP valido." % path)
    pack = JavaPack(path)
    pack.zf = zipfile.ZipFile(path, "r")
    rx = re.compile(r"^(.*?)assets/minecraft/textures/(.+)$", re.IGNORECASE)
    by_prefix = {}
    for info in pack.zf.infolist():
        if info.filename.endswith("/"):
            continue
        m = rx.match(info.filename)
        if m:
            by_prefix.setdefault(m.group(1), []).append((m.group(2), info.filename))
    if not by_prefix:
        pack.close()
        raise ValueError("Nao encontrei 'assets/minecraft/textures/' neste ZIP.")
    # Pack dentro de uma pasta: usa o prefixo com mais arquivos.
    pack.prefix = max(by_prefix, key=lambda k: len(by_prefix[k]))
    for rel, member in by_prefix[pack.prefix]:
        parts = rel.replace("\\", "/").split("/")
        folder = parts[0].lower()
        pack.dirs.add(folder)
        low = rel.lower()
        if folder in ("block", "blocks", "item", "items") and len(parts) == 2 \
                and low.endswith(IMG_EXTS):
            stem = os.path.splitext(parts[1])[0].lower()
            key = "%s/%s" % (folder, stem)
            # PNG tem prioridade sobre TGA quando existirem os dois.
            if key not in pack.members or low.endswith(".png"):
                pack.members[key] = member
        elif folder == "misc" and len(parts) == 2 and low.endswith(IMG_EXTS):
            pack.misc[os.path.splitext(parts[1])[0].lower()] = member
        else:
            pack.other.append(rel)
    snd_rx = re.compile(r"^" + re.escape(pack.prefix) +
                        r"assets/minecraft/sounds/(.+)\.(ogg|mp3|wav)$", re.IGNORECASE)
    for n in pack.zf.namelist():
        m = snd_rx.match(n)
        if m:
            pack.sounds[m.group(1).lower()] = (n, m.group(2).lower())
    sky_rx = re.compile(r"^" + re.escape(pack.prefix) +
                        r"assets/minecraft/(?:mcpatcher|optifine)/sky/world0/([^/]+\.png)$",
                        re.IGNORECASE)
    for n in pack.zf.namelist():
        m = sky_rx.match(n)
        if m:
            pack.sky[m.group(1).lower()] = n
    meta_name = (pack.prefix + "pack.mcmeta")
    for n in pack.zf.namelist():
        if n.lower() == meta_name.lower():
            try:
                pack.pack_meta = json.loads(pack.zf.read(n).decode("utf-8-sig"))
            except Exception:
                pack.pack_meta = {}
            break
    return pack


def _loads_lenient(raw):
    """JSON do Bedrock costuma ter BOM e comentarios //, /* */."""
    text = raw.decode("utf-8-sig")
    try:
        return json.loads(text)
    except ValueError:
        pass
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    text = "\n".join(l for l in text.splitlines() if not l.lstrip().startswith("//"))
    text = re.sub(r",(\s*[}\]])", r"\1", text)   # virgula sobrando
    return json.loads(text)


def _first_texture_path(entry):
    """Primeiro caminho em 'textures' de terrain_texture/item_texture.json."""
    tex = entry.get("textures") if isinstance(entry, dict) else None
    while isinstance(tex, list) and tex:
        tex = tex[0]
    if isinstance(tex, dict):
        tex = tex.get("path")
    return tex if isinstance(tex, str) else None


def read_bedrock_pack(path):
    """Le um Resource Pack Bedrock (.zip/.mcpack): textures/blocks, textures/items
    e as chaves de terrain_texture.json / item_texture.json."""
    if not zipfile.is_zipfile(path):
        raise ValueError("'%s' nao e um arquivo ZIP/MCPACK valido." % path)
    pack = JavaPack(path)
    pack.edition = "bedrock"
    pack.zf = zipfile.ZipFile(path, "r")
    rx = re.compile(r"^(.*?)textures/(blocks|items)/([^/]+)\.(png|tga)$", re.IGNORECASE)
    by_prefix, jsons = {}, {}
    for info in pack.zf.infolist():
        n = info.filename
        if n.endswith("/") or "assets/minecraft/" in n.lower():
            continue
        m = rx.match(n)
        if m:
            by_prefix.setdefault(m.group(1), []).append((m, n))
        low = n.lower()
        for jn in ("textures/terrain_texture.json", "textures/item_texture.json", "manifest.json"):
            if low.endswith(jn):
                jsons.setdefault(jn, []).append(n)
    if not by_prefix:
        pack.close()
        raise ValueError("Nao encontrei 'textures/blocks/' nem 'textures/items/' neste ZIP.")
    pack.prefix = max(by_prefix, key=lambda k: len(by_prefix[k]))
    files = {}
    for m, n in by_prefix[pack.prefix]:
        folder, stem, ext = m.group(2).lower(), m.group(3).lower(), m.group(4).lower()
        key = "%s/%s" % (folder, stem)
        if key not in pack.members or ext == "png":
            pack.members[key] = n
        files["textures/%s/%s" % (folder, stem)] = pack.members[key]
        pack.dirs.add(folder)
    for n in pack.zf.namelist():
        if n.endswith("/") or not n.startswith(pack.prefix):
            continue
        rel = n[len(pack.prefix):]
        if rel.lower().startswith("textures/") and not re.match(
                r"(?i)textures/(blocks|items|misc)/[^/]+\.(png|tga)$", rel):
            pack.other.append(rel[len("textures/"):])

    def read_json(jn):
        cands = [n for n in jsons.get(jn, []) if n.startswith(pack.prefix)]
        if not cands:
            return None
        try:
            return _loads_lenient(pack.zf.read(sorted(cands, key=len)[0]))
        except Exception as exc:
            pack.warnings.append("nao consegui ler %s (%s); usando nomes de arquivo" % (jn, exc))
            return None

    brx = re.compile(r"^" + re.escape(pack.prefix) + r"textures/misc/([^/]+)\.(png|tga)$", re.IGNORECASE)
    srx = re.compile(r"^" + re.escape(pack.prefix) + r"sounds/(.+)\.(ogg|mp3|wav|fsb)$", re.IGNORECASE)
    for n in pack.zf.namelist():
        m = brx.match(n)
        if m:
            pack.misc[m.group(1).lower()] = n
        m = srx.match(n)
        if m:
            pack.sounds[m.group(1).lower()] = (n, m.group(2).lower())
    pack.manifest = read_json("manifest.json") or {}
    for jn, folder in (("textures/terrain_texture.json", "blocks"),
                       ("textures/item_texture.json", "items")):
        data = read_json(jn)
        if not isinstance(data, dict):
            continue
        for key, entry in (data.get("texture_data") or {}).items():
            tp = _first_texture_path(entry)
            if not tp:
                continue
            member = files.get(tp.lower().replace("\\", "/"))
            if member:   # a chave do JSON passa a valer como nome da textura
                pack.members["%s/%s" % (folder, key.lower())] = member
    return pack


def read_pack(path, edition="auto"):
    """Escolhe leitor Java ou Bedrock (auto = detecta pelo conteudo do ZIP)."""
    if edition == "java":
        return read_java_pack(path)
    if edition == "bedrock":
        return read_bedrock_pack(path)
    if not zipfile.is_zipfile(path):
        raise ValueError("'%s' nao e um arquivo ZIP valido." % path)
    with zipfile.ZipFile(path) as z:
        low = [n.lower() for n in z.namelist()]
    if any("assets/minecraft/textures/" in n for n in low):
        return read_java_pack(path)
    if any(re.search(r"(^|/)textures/(blocks|items)/", n) for n in low):
        return read_bedrock_pack(path)
    raise ValueError("Nao reconheci o pack: nem Java (assets/minecraft/textures/) "
                     "nem Bedrock (textures/blocks|items/).")


def detect_version(pack):
    """Detecta layout (antigo 'blocks/items' x novo 'block/item') e pack_format."""
    if pack.edition == "bedrock":
        hdr = (pack.manifest or {}).get("header", {}) if isinstance(pack.manifest, dict) else {}
        eng = hdr.get("min_engine_version")
        return {"layout": "bedrock", "pack_format": None,
                "versao_java_aproximada": "n/a (Bedrock; min_engine_version=%s)" % (
                    ".".join(str(x) for x in eng) if isinstance(eng, list) else eng),
                "pastas_de_blocos": ["blocks"], "pastas_de_itens": ["items"]}
    legacy = bool(pack.dirs & {"blocks", "items"})
    modern = bool(pack.dirs & {"block", "item"})
    if modern and legacy:
        layout = "misto"
    elif modern:
        layout = "flattened (1.13+)"
    elif legacy:
        layout = "antigo (<=1.12)"
    else:
        layout = "desconhecido"
    fmt = None
    try:
        fmt = int(pack.pack_meta.get("pack", {}).get("pack_format"))
    except (TypeError, ValueError, AttributeError):
        pass
    block_dirs = ["block", "blocks"] if modern or not legacy else ["blocks", "block"]
    item_dirs = ["item", "items"] if modern or not legacy else ["items", "item"]
    if modern and legacy:
        block_dirs, item_dirs = ["block", "blocks"], ["item", "items"]
    return {
        "layout": layout,
        "pack_format": fmt,
        "versao_java_aproximada": PACK_FORMATS.get(fmt, "desconhecida") if fmt else "desconhecida",
        "pastas_de_blocos": block_dirs,
        "pastas_de_itens": item_dirs,
    }


# ------------------------------------------------------ referencia do Blockman
class BlockmanReference(object):
    def __init__(self, blocks, items_png, items_json_bytes, items_json):
        self.blocks = blocks                  # nome -> {"w","h"}
        self.items_png = items_png            # PIL RGBA
        self.items_json_bytes = items_json_bytes
        self.items_frames = items_json["frames"]


def load_internal_blockman_reference():
    """Carrega a referencia embutida. NAO usa nenhum ZIP do Blockman GO."""
    need = ["blocks_manifest.json", "items.png", "items.json"]
    missing = [n for n in need if not (REF_DIR / n).is_file()]
    if missing:
        raise FileNotFoundError(
            "Arquivos internos ausentes em %s: %s. Reinstale o programa completo."
            % (REF_DIR, ", ".join(missing)))
    manifest = json.loads((REF_DIR / "blocks_manifest.json").read_text(encoding="utf-8"))
    raw = (REF_DIR / "items.json").read_bytes()
    atlas = Image.open(str(REF_DIR / "items.png")).convert("RGBA")
    frames = json.loads(raw.decode("utf-8"))
    meta = frames.get("meta", {}).get("size", {})
    if (meta.get("w"), meta.get("h")) != atlas.size:
        raise ValueError("items.json e items.png internos nao batem (%s x %s)."
                         % (meta, atlas.size))
    return BlockmanReference(manifest["blocks"], atlas, raw, frames)


def build_texture_mapping(ref, edition="java"):
    """Filtra as tabelas contra a referencia real (nada de nomes inventados)."""
    blocks, items, warnings = OrderedDict(), OrderedDict(), []
    for name, cands in sorted(bg_mappings.BLOCKS.items()):
        if name in ref.blocks:
            blocks[name] = list(cands)
        else:
            warnings.append("mapeamento de bloco ignorado (nome inexistente no Blockman): " + name)
    for name, cands in sorted(bg_mappings.ITEMS.items()):
        if name in ref.items_frames:
            items[name] = list(cands)
        else:
            warnings.append("mapeamento de item ignorado (sprite inexistente no atlas): " + name)
    opaque = OrderedDict()
    for name, src in sorted(bg_mappings.OPAQUE_LEAVES.items()):
        if name in ref.blocks and src in blocks:
            opaque[name] = src
        else:
            warnings.append("folha opaca ignorada: " + name)
    if edition == "bedrock":
        # Os nomes do Bedrock sao em grande parte iguais aos do Blockman:
        # tenta o nome IDENTICO primeiro, depois os aliases ja conhecidos.
        for name in ref.blocks:
            if name in bg_mappings.UNSUPPORTED_BLOCKS:
                continue
            blocks[name] = [name] + [c for c in blocks.get(name, []) if c != name]
        for name in ref.items_frames:
            items[name] = [name] + [c for c in items.get(name, []) if c != name]
    return {"blocks": blocks, "items": items, "opaque": opaque, "warnings": warnings}


# ------------------------------------------------------------ imagem
def _png_bytes(im):
    buf = io.BytesIO()
    im.save(buf, "PNG")
    return buf.getvalue()


def _frame_count(im):
    """Quantos quadros quadrados tem a imagem (tira vertical estilo .mcmeta)."""
    w, h = im.size
    if w > 0 and h >= w and h % w == 0:
        return h // w
    return 0


def _scale(im, size):
    if im.size == tuple(size):
        return im
    return im.resize(tuple(size), NEAREST)


def _fit_into_frame(im, fw, fh):
    """Ajusta sprite ao frame do atlas.

    Mesma proporcao  -> resize NEAREST direto.
    Proporcao diferente -> maior escala inteira que cabe, centralizado e com
    transparencia ao redor (nada e esticado/distorcido).
    Retorna (imagem_fw_x_fh, descricao).
    """
    w, h = im.size
    if (w, h) == (fw, fh):
        return im, "mesmo_tamanho"
    if w * fh == h * fw:
        return im.resize((fw, fh), NEAREST), "redimensionado"
    scale = min(fw // w if w else 0, fh // h if h else 0)
    if scale >= 1:
        sp = im.resize((w * scale, h * scale), NEAREST)
    else:  # sprite maior que o frame: reduz proporcionalmente
        f = min(fw / float(w), fh / float(h))
        sp = im.resize((max(1, int(w * f)), max(1, int(h * f))), NEAREST)
    canvas = Image.new("RGBA", (fw, fh), (0, 0, 0, 0))
    canvas.paste(sp, ((fw - sp.size[0]) // 2, (fh - sp.size[1]) // 2))
    return canvas, "redimensionado_e_centralizado"


def _find_source(pack, dirs, candidates):
    for cand in candidates:
        for folder in dirs:
            if pack.has(folder, cand):
                return folder, cand
    return None


# ------------------------------------------------------------ blocos
def _make_block(pack, found, target_w, target_h):
    """Converte uma textura de bloco. Retorna (img, acao) ou levanta ValueError."""
    folder, stem = found
    src = pack.load(folder, stem)
    sw, sh = src.size
    n_target = target_h // target_w if target_w and target_h % target_w == 0 else 0
    if target_w == target_h:                      # textura estatica 64x64
        if sw == sh:
            acao = "redimensionado" if sw != target_w else "reencodado_rgba_mesmo_tamanho"
            return _scale(src, (target_w, target_h)), acao
        if _frame_count(src) > 1:                 # animada no Java: 1o frame
            first = src.crop((0, 0, sw, sw))
            return _scale(first, (target_w, target_h)), "primeiro_frame_de_animacao"
        raise ValueError("origem nao quadrada (%dx%d) e nao e tira de frames" % (sw, sh))
    # destino e tira animada (ex.: sea_lantern, prismarine_rough)
    fc = _frame_count(src)
    if fc != n_target:
        raise ValueError("quantidade de frames incompativel: origem %d (%dx%d), destino %d"
                         % (fc, sw, sh, n_target))
    out = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
    for i in range(fc):
        frame = src.crop((0, i * sw, sw, (i + 1) * sw))
        out.paste(_scale(frame, (target_w, target_w)), (0, i * target_w))
    return out, "tira_animada_redimensionada"


def _make_opaque(im):
    """Folha 'opaque' do Blockman: sem alpha. Buracos recebem a cor media das
    partes opacas (heuristica; a referencia usa tons proprios nos buracos)."""
    px = im.load()
    w, h = im.size
    r = g = b = n = 0
    for y in range(h):
        for x in range(w):
            p = px[x, y]
            if p[3] >= 128:
                r += p[0]; g += p[1]; b += p[2]; n += 1
    avg = (r // n, g // n, b // n) if n else (0, 0, 0)
    out = Image.new("RGBA", im.size)
    po = out.load()
    for y in range(h):
        for x in range(w):
            p = px[x, y]
            po[x, y] = (p[0], p[1], p[2], 255) if p[3] >= 128 else (avg[0], avg[1], avg[2], 255)
    return out


def convert_blocks(pack, ref, mapping, version, report):
    outputs = OrderedDict()
    used_java = set()
    detail = {}
    done = {}
    for bg_name, cands in mapping["blocks"].items():
        found = _find_source(pack, version["pastas_de_blocos"], cands)
        if not found:
            if bg_name not in mapping["opaque"]:   # opacas ainda podem ser derivadas
                report["sem_correspondencia"]["blocos_blockman_sem_textura_no_pack"].append(bg_name)
            continue
        ref_sz = ref.blocks[bg_name]
        try:
            img, acao = _make_block(pack, found, ref_sz["w"], ref_sz["h"])
        except ValueError as exc:
            report["incompativeis"].append({"destino": bg_name,
                                            "origem": "%s/%s" % found, "motivo": str(exc)})
            continue
        except Exception as exc:  # imagem corrompida, formato ilegivel...
            report["erros"].append({"destino": bg_name, "origem": "%s/%s" % found,
                                    "erro": "%s: %s" % (type(exc).__name__, exc)})
            continue
        outputs[OUT_BLOCKS_DIR + bg_name + ".png"] = _png_bytes(img)
        used_java.add("%s/%s" % found)
        done[bg_name] = img
        detail[acao] = detail.get(acao, 0) + 1
        if bg_name in ("dirt_new", "dirt_top", "glass_new"):
            detail["alias"] = detail.get("alias", 0) + 1
    # folhas opacas (derivadas)
    for bg_name, src_name in mapping["opaque"].items():
        if bg_name in done:
            continue   # veio direto do pack (ex.: Bedrock tem leaves_*_opaque)
        if src_name not in done:
            report["sem_correspondencia"]["blocos_blockman_sem_textura_no_pack"].append(bg_name)
            continue
        outputs[OUT_BLOCKS_DIR + bg_name + ".png"] = _png_bytes(_make_opaque(done[src_name]))
        detail["derivado_folha_opaca"] = detail.get("derivado_folha_opaca", 0) + 1
    report["blocos_detalhe"] = detail
    report["_used_java"] |= used_java
    return outputs


# ------------------------------------------------------------ itens
def _frame_box(ref, name):
    f = ref.items_frames[name]["frame"]
    return (f["x"], f["y"], f["x"] + f["w"], f["y"] + f["h"])


def _overlaps(a, b):
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


def convert_items(pack, ref, mapping, version, report):
    """Substitui SOMENTE a regiao de cada sprite com correspondencia.

    O atlas do Blockman tem sprites que compartilham a MESMA regiao (ex.: os
    overlays de couro) ou se sobrepoem parcialmente. Escrever nessas regioes
    alteraria outros sprites, entao so escrevemos quando e seguro.
    """
    atlas = ref.items_png.copy()
    boxes = dict((n, _frame_box(ref, n)) for n in ref.items_frames)
    by_box = {}
    for n, b in boxes.items():
        by_box.setdefault(b, []).append(n)
    # 1) resolve a origem Java de cada sprite mapeado
    resolved = {}
    for bg_name, cands in mapping["items"].items():
        found = _find_source(pack, version["pastas_de_itens"], cands)
        if not found:
            report["sem_correspondencia"]["itens_blockman_sem_textura_no_pack"].append(bg_name)
        else:
            resolved[bg_name] = found
    replaced = []
    detail = {}
    for bg_name, found in sorted(resolved.items()):
        box = boxes[bg_name]
        same_region = by_box[box]
        partial = sorted(n for n, b in boxes.items()
                         if n != bg_name and b != box and _overlaps(box, b))
        if partial:
            report["incompativeis"].append({
                "destino": "item:" + bg_name, "origem": "%s/%s" % found,
                "motivo": "regiao do atlas se sobrepoe parcialmente a: " + ", ".join(partial)
                          + " (escrever corromperia outros sprites)"})
            continue
        if len(same_region) > 1:
            sources = set(resolved.get(n) for n in same_region)
            if None in sources or len(sources) > 1:
                report["incompativeis"].append({
                    "destino": "item:" + bg_name, "origem": "%s/%s" % found,
                    "motivo": "regiao do atlas compartilhada com: "
                              + ", ".join(n for n in same_region if n != bg_name)
                              + " (fontes diferentes ou sem fonte; nao sobrescrito)"})
                continue
        x, y, fw, fh = box[0], box[1], box[2] - box[0], box[3] - box[1]
        try:
            src = pack.load(*found)
            if src.size[1] > src.size[0] and src.size[1] % src.size[0] == 0:
                src = src.crop((0, 0, src.size[0], src.size[0]))  # 1o frame
            sprite, acao = _fit_into_frame(src, fw, fh)
        except ValueError as exc:
            report["incompativeis"].append({"destino": "item:" + bg_name,
                                            "origem": "%s/%s" % found, "motivo": str(exc)})
            continue
        except Exception as exc:
            report["erros"].append({"destino": "item:" + bg_name, "origem": "%s/%s" % found,
                                    "erro": "%s: %s" % (type(exc).__name__, exc)})
            continue
        atlas.paste(sprite, (x, y))  # sem mascara: substitui pixels e alpha da regiao
        replaced.append(bg_name)
        report["_used_java"].add("%s/%s" % found)
        detail[acao] = detail.get(acao, 0) + 1
    report["itens_detalhe"] = detail
    outputs = OrderedDict()
    if replaced:
        outputs[OUT_ITEMS_DIR + "items.png"] = _png_bytes(atlas)
        outputs[OUT_ITEMS_DIR + "items.json"] = ref.items_json_bytes  # intacto
    report["itens_substituidos"] = sorted(replaced)
    report["itens_sprites_preservados"] = len(ref.items_frames) - len(replaced)
    return outputs


# ------------------------------------------------- categorias futuras (stubs)
def convert_entities(pack, ref, report):
    """Ainda nao implementado: nao gera nada e nao conta como convertido."""
    return OrderedDict()


def convert_environment(pack, ref, report):
    """Converte SOMENTE o skybox (faces de ceu). Sol/lua/nuvens ainda nao."""
    outputs = OrderedDict()
    done = []
    groups = {}
    for fname in pack.sky:
        m = re.match(r"^(cloud|starfield)(\d*)\.png$", fname)
        if m:
            groups.setdefault(m.group(1), []).append((int(m.group(2) or 0), fname))
    report["skybox"] = {"convertidos": [], "incompativeis": [], "nao_usados": []}
    for kind, files in sorted(groups.items()):
        files.sort()
        folder, prefix = bg_mappings.SKY_SOURCES[kind]
        fname = files[0][1]
        report["skybox"]["nao_usados"].extend(f for _, f in files[1:])
        try:
            im = Image.open(io.BytesIO(pack.zf.read(pack.sky[fname]))).convert("RGBA")
            w, h = im.size
            if abs(w * 2 - h * 3) > max(3, w // 100):
                raise ValueError("imagem %dx%d nao e grade 3x2 (proporcao 3:2)" % (w, h))
            cw, ch = w // 3, h // 2
            faces = {}
            for r, row in enumerate(bg_mappings.SKY_GRID_3X2):
                for c, face in enumerate(row):
                    cell = im.crop((c * cw, r * ch, (c + 1) * cw, (r + 1) * ch))
                    if face in ("top", "bottom"):
                        cell = cell.rotate(360)
                    # Preserva a resolucao original do recorte. Nao reduzir para
                    # SKY_FACE_SIZE (682): um atlas 6144x4096 gera faces 2048x2048.
                    faces[bg_mappings.SKY_FACE_TO_BG[face]] = cell
        except ValueError as exc:
            report["skybox"]["incompativeis"].append({"origem": fname, "motivo": str(exc)})
            report["incompativeis"].append({"destino": "skybox/" + folder,
                                            "origem": "sky/world0/" + fname, "motivo": str(exc)})
            continue
        except Exception as exc:
            report["erros"].append({"destino": "skybox/" + folder, "origem": fname,
                                    "erro": "%s: %s" % (type(exc).__name__, exc)})
            continue
        for suffix, cell in faces.items():
            # O jogo espera os dois nomes lado a lado. Neste projeto, .png.ktx
            # e uma copia binaria do PNG (nao uma codificacao KTX real).
            png_data = _png_bytes(cell)
            png_name = "Media/Textures/skybox/%s/%s_%s.png" % (folder, prefix, suffix)
            outputs[png_name] = png_data
            outputs[png_name + ".ktx"] = png_data
        done.append("%s -> skybox/%s (%dx%d, 6 faces)" % (fname, folder, w, h))
    report["skybox"]["convertidos"] = done
    if done:
        report["avisos"].append(
            "Skybox: layout 3x2 e correspondencia cloud->sunny / starfield->stars "
            "sao SUPOSICOES nao validadas; arquivos .png.ktx sao copias binarias "
            "dos PNGs, nao KTX verdadeiros.")
    return outputs


MISC_TARGETS = [  # (candidatos no pack, destino no Blockman)
    (["enchanted_item_glint", "enchanted_glint_item"], "Media/misc/enchanted_item_glint.png"),
]
HURT_TARGETS = ["Media/Sound/random/boy_hurt.mp3", "Media/Sound/random/girl_hurt.mp3"]


def convert_misc(pack, ref, report):
    """Item glint (brilho de encantamento). Tamanho do alvo NAO e conhecido
    (nao existe no ZIP de referencia): mantem o tamanho do pack, so garante RGBA."""
    outputs = OrderedDict()
    rep = report["misc"] = {"convertidos": [], "sem_correspondencia": [], "erros": []}
    for cands, dest in MISC_TARGETS:
        stem = next((c for c in cands if c in pack.misc), None)
        if stem is None:
            rep["sem_correspondencia"].append(dest)
            continue
        try:
            im = Image.open(io.BytesIO(pack.zf.read(pack.misc[stem]))).convert("RGBA")
        except Exception as exc:
            report["erros"].append({"destino": dest, "origem": "misc/" + stem,
                                    "erro": "%s: %s" % (type(exc).__name__, exc)})
            continue
        outputs[dest] = _png_bytes(im)
        rep["convertidos"].append("misc/%s (%dx%d) -> %s" % (stem, im.size[0], im.size[1], dest))
    if rep["convertidos"]:
        report["avisos"].append(
            "Item glint: tamanho esperado pelo Blockman nao validado (mantido o do pack) e "
            "enchanted_item_glint.png.ktx NAO e gerado.")
    return outputs


def _to_mp3(data, ext):
    """ogg/wav -> mp3 44.1kHz estereo 128k (mesmo formato do boy_hurt.mp3 de referencia)."""
    ff = shutil.which("ffmpeg")
    if not ff:
        raise EnvironmentError("ffmpeg nao encontrado (no Termux: pkg install ffmpeg)")
    tmp = tempfile.mkdtemp(prefix="mcbg_")
    try:
        src, dst = os.path.join(tmp, "in." + ext), os.path.join(tmp, "out.mp3")
        with open(src, "wb") as fh:
            fh.write(data)
        proc = subprocess.run(
            [ff, "-v", "error", "-y", "-i", src, "-vn", "-map_metadata", "-1",
             "-codec:a", "libmp3lame", "-b:a", "128k", "-ar", "44100", "-ac", "2", dst],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=120)
        if proc.returncode != 0 or not os.path.isfile(dst):
            raise ValueError("ffmpeg falhou: " + proc.stderr.decode("utf-8", "replace")[:200])
        with open(dst, "rb") as fh:
            return fh.read()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def convert_sounds(pack, report, hit=1):
    """Som de dano/hit: damage/hit<N> -> boy_hurt.mp3 e girl_hurt.mp3.

    O Java so tem um conjunto (hit1-3); boy e girl recebem o MESMO audio
    (na referencia os dois tem formato/duracao identicos)."""
    outputs = OrderedDict()
    rep = report["sons"] = {"convertidos": [], "copiados_sem_processar": [],
                            "nao_convertidos": [], "sem_correspondencia": []}
    order = ["damage/hit%d" % hit] + ["damage/hit%d" % n for n in (1, 2, 3) if n != hit]
    key = next((k for k in order if k in pack.sounds), None)
    if key is None:
        rep["sem_correspondencia"].append("damage/hit1..3")
        return outputs
    member, ext = pack.sounds[key]
    try:
        raw = pack.zf.read(member)
        if ext == "mp3":
            data, bucket = raw, "copiados_sem_processar"
        elif ext in ("ogg", "wav"):
            data, bucket = _to_mp3(raw, ext), "convertidos"
        else:
            raise ValueError("formato de audio '%s' nao suportado" % ext)
    except EnvironmentError as exc:
        rep["nao_convertidos"].append({"origem": key, "motivo": str(exc)})
        report["incompativeis"].append({"destino": "sons/hurt", "origem": key, "motivo": str(exc)})
        return outputs
    except ValueError as exc:
        rep["nao_convertidos"].append({"origem": key, "motivo": str(exc)})
        report["incompativeis"].append({"destino": "sons/hurt", "origem": key, "motivo": str(exc)})
        return outputs
    except Exception as exc:
        report["erros"].append({"destino": "sons/hurt", "origem": key,
                                "erro": "%s: %s" % (type(exc).__name__, exc)})
        return outputs
    for dest in HURT_TARGETS:
        outputs[dest] = data
        rep[bucket].append("%s.%s -> %s" % (key, ext, dest))
    report["avisos"].append(
        "Som de hit: boy_hurt e girl_hurt recebem o mesmo audio (%s); escolha outro com --hit-sound 1|2|3." % key)
    return outputs


# ------------------------------------------------------------ saida
def generate_output_structure(outputs, out_zip, root=""):
    prefix = (root.strip("/") + "/") if root.strip("/") else ""
    tmp = str(out_zip) + ".tmp"
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, data in outputs.items():
            zf.writestr(prefix + name, data)
    os.replace(tmp, str(out_zip))


def generate_report(report, path):
    clean = {k: v for k, v in report.items() if not k.startswith("_")}
    with open(str(path), "w", encoding="utf-8") as fh:
        json.dump(clean, fh, ensure_ascii=False, indent=2)


# ------------------------------------------------------------ principal
def _new_report(in_path):
    return {
        "entrada": os.path.basename(in_path),
        "edicao": None,
        "versao_detectada": {},
        "resumo": {},
        "blocos_detalhe": {},
        "itens_detalhe": {},
        "itens_substituidos": [],
        "sem_correspondencia": {
            "blocos_blockman_sem_textura_no_pack": [],
            "itens_blockman_sem_textura_no_pack": [],
            "texturas_java_sem_uso": [],
        },
        "sem_regra_de_mapeamento": {"blocos_blockman": []},
        "nao_suportados_ainda": {},
        "incompativeis": [],
        "erros": [],
        "ignorados": {},
        "categorias_nao_convertidas": dict(CATEGORIES_NOT_SUPPORTED),
        "avisos": [
            "Compatibilidade NAO validada dentro do Blockman GO: teste o ZIP no jogo.",
            "Nomes de destino vem do ZIP de referencia usado no desenvolvimento.",
        ],
        "_used_java": set(),
    }


def run(in_path, out_path, root="", force=False, edition="auto", hit=1):
    out_path = Path(out_path)
    report_path = out_path.with_name(out_path.stem + "_relatorio.json")
    if (out_path.exists() or report_path.exists()) and not force:
        raise FileExistsError("'%s' ou o relatorio ja existe. Use --force para sobrescrever."
                              % out_path)
    report = _new_report(in_path)
    ref = load_internal_blockman_reference()
    pack = read_pack(in_path, edition)
    try:
        report["edicao"] = pack.edition
        report["avisos"].extend(pack.warnings)
        version = detect_version(pack)
        report["versao_detectada"] = {k: version[k] for k in
                                      ("layout", "pack_format", "versao_java_aproximada")}
        mapping = build_texture_mapping(ref, pack.edition)
        report["avisos"].extend(mapping["warnings"])
        outputs = OrderedDict()
        outputs.update(convert_blocks(pack, ref, mapping, version, report))
        outputs.update(convert_items(pack, ref, mapping, version, report))
        outputs.update(convert_entities(pack, ref, report))
        outputs.update(convert_environment(pack, ref, report))
        outputs.update(convert_misc(pack, ref, report))
        outputs.update(convert_sounds(pack, report, hit))

        mapped = set(mapping["blocks"]) | set(mapping["opaque"])
        report["sem_regra_de_mapeamento"]["blocos_blockman"] = sorted(
            n for n in ref.blocks if n not in mapped and n not in bg_mappings.UNSUPPORTED_BLOCKS)
        report["nao_suportados_ainda"] = {n: bg_mappings.UNSUPPORTED_BLOCKS[n]
                                          for n in sorted(bg_mappings.UNSUPPORTED_BLOCKS)
                                          if n in ref.blocks}
        used = report["_used_java"]
        report["sem_correspondencia"]["texturas_java_sem_uso"] = sorted(
            k for k in pack.members if k not in used)
        ign = {}
        for rel in pack.other:
            top = rel.split("/")[0].lower() if "/" in rel else "(raiz)"
            ign[top] = ign.get(top, 0) + 1
        report["ignorados"] = {"por_pasta_fora_de_block_item": ign,
                               "texturas_block_item_sem_uso": len(
                                   report["sem_correspondencia"]["texturas_java_sem_uso"])}
        n_blocks = sum(1 for k in outputs if k.startswith(OUT_BLOCKS_DIR))
        report["resumo"] = {
            "blocos_convertidos": n_blocks,
            "itens_convertidos": len(report["itens_substituidos"]),
            "texturas_incompativeis": len(report["incompativeis"]),
            "erros": len(report["erros"]),
            "skyboxes_convertidos": len(report["skybox"]["convertidos"]),
            "item_glint_convertido": len(report["misc"]["convertidos"]),
            "sons_hurt_convertidos": len(report["sons"]["convertidos"]),
            "sons_hurt_copiados_sem_processar": len(report["sons"]["copiados_sem_processar"]),
        }
        if not outputs:
            raise ValueError("Nenhuma textura reconhecida: nada a gerar. "
                             "Veja o relatorio de versao/layout.")
        generate_output_structure(outputs, out_path, root)
        generate_report(report, report_path)
    finally:
        pack.close()
    return out_path, report_path, report


def _default_output(in_path):
    return Path(os.getcwd()) / (Path(in_path).stem + "_bg.zip")


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Converte Resource Pack Minecraft Java em texturas Blockman GO.")
    ap.add_argument("entrada", help="ZIP do Resource Pack do Minecraft Java")
    ap.add_argument("saida", nargs="?", help="ZIP de saida (padrao: <entrada>_bg.zip)")
    ap.add_argument("--root", default="",
                    help="pasta raiz dentro do ZIP de saida (ex.: BlockManGoTXT). Padrao: nenhuma")
    ap.add_argument("--edition", choices=["auto", "java", "bedrock"], default="auto",
                    help="edicao do pack de entrada (padrao: detectar automaticamente)")
    ap.add_argument("--hit-sound", type=int, choices=[1, 2, 3], default=1,
                    help="qual damage/hit<N> do pack vira boy_hurt/girl_hurt (padrao: 1)")
    ap.add_argument("--force", action="store_true", help="sobrescrever saida existente")
    args = ap.parse_args(argv)
    if not os.path.isfile(args.entrada):
        sys.exit("Arquivo nao encontrado: %s" % args.entrada)
    out = args.saida or _default_output(args.entrada)
    try:
        out_zip, rep_path, rep = run(args.entrada, out, args.root, args.force, args.edition, args.hit_sound)
    except (ValueError, FileExistsError, FileNotFoundError) as exc:
        sys.exit("Erro: %s" % exc)
    r = rep["resumo"]
    print("Edicao: %s" % rep.get("edicao"))
    print("Versao/layout: %s | pack_format=%s (%s)" % (
        rep["versao_detectada"]["layout"], rep["versao_detectada"]["pack_format"],
        rep["versao_detectada"]["versao_java_aproximada"]))
    print("Blocos convertidos : %d" % r["blocos_convertidos"])
    print("Itens convertidos  : %d" % r["itens_convertidos"])
    print("Skybox: %d | Item glint: %d | Sons hit: %d" % (
        r["skyboxes_convertidos"], r["item_glint_convertido"],
        r["sons_hurt_convertidos"] + r["sons_hurt_copiados_sem_processar"]))
    print("Incompativeis      : %d | Erros: %d" % (r["texturas_incompativeis"], r["erros"]))
    print("ZIP      : %s" % out_zip)
    print("Relatorio: %s" % rep_path)
    print("Aviso: compatibilidade nao validada no jogo — teste no Blockman GO.")


if __name__ == "__main__":
    main()
