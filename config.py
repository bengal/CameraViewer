from dataclasses import dataclass, field
from typing import List
import os
import configparser

@dataclass
class CamConfig:
    url: str
    preview_url: str
    description: str
    index: int
    proto: str

@dataclass
class CamViewerConfig:
    columns: int = 2
    cameras: List[CamConfig] = field(default_factory=list)

def read_config():
    conf_files = [ "camviewer.conf", os.path.expanduser('~/.camviewer.conf') ]

    for f in conf_files:
        if not os.path.exists(f):
            continue
        
        camviewer_config = CamViewerConfig()
        parser = configparser.ConfigParser()
        parser.read(f)

        camviewer_config.columns = parser.getint("main", "GridColumns", fallback = camviewer_config.columns)
        
        for i in range(1, 32):
            section_name = "camera{}".format(i)
            if section_name not in parser:
                break
            section = parser[section_name]
            if section is None:
                break
            url = section.get("url", None)
            if url is None:
                break
            preview_url = section.get("PreviewUrl", None)
            desc = section.get("Description", None)
            proto = section.get("Protocol", None)
            camera = CamConfig(url=url, preview_url=preview_url, description=desc, index=i, proto=proto)
            camviewer_config.cameras.append(camera)

        return camviewer_config

    return None

