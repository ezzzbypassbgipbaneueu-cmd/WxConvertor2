# -*- coding: utf-8 -*-
"""Ponte entre o app Android (Kotlin) e o conversor mc_to_blockman.

Gera SOMENTE o .zip do Blockman GO. O relatorio .json que o conversor cria
internamente e apagado; so um resumo em texto volta para a tela do app.
"""
import os
from pathlib import Path

import mc_to_blockman as m


def convert(in_path, out_dir, out_name, ref_dir):
    m.REF_DIR = Path(ref_dir)          # referencia copiada dos assets pelo app
    out = Path(out_dir) / out_name
    zip_path, rep_path, rep = m.run(in_path, out, force=True)
    try:
        os.remove(str(rep_path))       # nada de .json na saida
    except OSError:
        pass

    r = rep["resumo"]
    v = rep.get("versao_detectada") or {}
    linhas = [
        "Edição: %s" % rep.get("edicao"),
        "Versão/layout: %s (pack_format %s, %s)" % (
            v.get("layout"), v.get("pack_format"), v.get("versao_java_aproximada")),
        "Blocos convertidos: %d" % r["blocos_convertidos"],
        "Itens convertidos: %d" % r["itens_convertidos"],
        "Skybox: %d | Item glint: %d | Sons hit: %d" % (
            r["skyboxes_convertidos"], r["item_glint_convertido"],
            r["sons_hurt_convertidos"] + r["sons_hurt_copiados_sem_processar"]),
        "Incompatíveis: %d | Erros: %d" % (r["texturas_incompativeis"], r["erros"]),
        "",
        "Compatibilidade não validada no jogo: teste no Blockman GO.",
    ]
    return str(zip_path), "\n".join(linhas)
