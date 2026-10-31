"""Controlled vocabulary of the thematic axes.

A document is counted in an axis when its title, abstract or keywords contain
at least one of the terms of that axis, so a document may be counted in more
than one axis. Matching is case-insensitive and by substring. The axis names
are in Portuguese, the language of the study; the order of the dictionary is
the order of the axes in the radar chart.
"""

THEMES = {
    "Aprendizado profundo": ["deep learning", "neural network", "cnn", "convolutional"],
    "Detecção de frutos/cachos": ["fruit detection", "bunch detection", "grape detection",
                                  "berry detection", "cluster detection"],
    "Uvas e vinhedos": ["grape", "vine", "vineyard", "vitis", "viticulture", "winemaking", "wine"],
    "Modelos leves/embarcados": ["lightweight", "embedded", "edge", "mobile", "efficient", "yolo",
                                 "real-time"],
    "YOLO": ["yolo", "you only look once"],
    "Robótica agrícola": ["robot", "uav", "drone", "autonomous", "platform"],
    "Segmentação": ["segmentation", "instance", "mask", "semantic"],
    "Viticultura de precisão": ["precision viticulture", "precision agriculture", "smart farming",
                                "iot"],
    "Estimativa de produtividade": ["yield estimation", "yield prediction", "crop yield",
                                    "production estimation", "biomass"],
    "Visão computacional": ["computer vision", "image processing", "object detection",
                            "feature extraction"],
}

# Line breaks used in the chart labels.
CHART_LABELS = {
    "Aprendizado profundo": "Aprendizado\nprofundo",
    "Detecção de frutos/cachos": "Detecção de\nfrutos/cachos",
    "Uvas e vinhedos": "Uvas e\nvinhedos",
    "Modelos leves/embarcados": "Modelos leves/\nembarcados",
    "Robótica agrícola": "Robótica\nagrícola",
    "Viticultura de precisão": "Viticultura de\nprecisão",
    "Estimativa de produtividade": "Estimativa de\nprodutividade",
    "Visão computacional": "Visão\ncomputacional",
}
