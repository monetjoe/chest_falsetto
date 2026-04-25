import os
import torch
import shutil
import librosa
import warnings
import numpy as np
import gradio as gr
import librosa.display
import matplotlib.pyplot as plt
from collections import Counter
from model import EvalNet
from utils import (
    get_modelist,
    find_files,
    embed_img,
    _L,
    SAMPLE_RATE,
    TEMP_DIR,
    TRANSLATE,
    CLASSES,
)


def wav2mel(audio_path: str, width=0.496145124716553):
    y, sr = librosa.load(audio_path, sr=SAMPLE_RATE)
    mel_spec = librosa.feature.melspectrogram(y=y, sr=sr)
    log_mel_spec = librosa.power_to_db(mel_spec, ref=np.max)
    dur = librosa.get_duration(y=y, sr=sr)
    total_frames = log_mel_spec.shape[1]
    step = int(width * total_frames / dur)
    count = int(total_frames / step)
    begin = int(0.5 * (total_frames - count * step))
    end = begin + step * count
    for i in range(begin, end, step):
        librosa.display.specshow(log_mel_spec[:, i : i + step])
        plt.axis("off")
        plt.savefig(
            f"{TEMP_DIR}/{i}.jpg",
            bbox_inches="tight",
            pad_inches=0.0,
        )
        plt.close()


def wav2cqt(audio_path: str, width=0.496145124716553):
    y, sr = librosa.load(audio_path, sr=SAMPLE_RATE)
    cqt_spec = librosa.cqt(y=y, sr=sr)
    log_cqt_spec = librosa.power_to_db(np.abs(cqt_spec) ** 2, ref=np.max)
    dur = librosa.get_duration(y=y, sr=sr)
    total_frames = log_cqt_spec.shape[1]
    step = int(width * total_frames / dur)
    count = int(total_frames / step)
    begin = int(0.5 * (total_frames - count * step))
    end = begin + step * count
    for i in range(begin, end, step):
        librosa.display.specshow(log_cqt_spec[:, i : i + step])
        plt.axis("off")
        plt.savefig(
            f"{TEMP_DIR}/{i}.jpg",
            bbox_inches="tight",
            pad_inches=0.0,
        )
        plt.close()


def wav2chroma(audio_path: str, width=0.496145124716553):
    y, sr = librosa.load(audio_path, sr=SAMPLE_RATE)
    chroma_spec = librosa.feature.chroma_stft(y=y, sr=sr)
    log_chroma_spec = librosa.power_to_db(np.abs(chroma_spec) ** 2, ref=np.max)
    dur = librosa.get_duration(y=y, sr=sr)
    total_frames = log_chroma_spec.shape[1]
    step = int(width * total_frames / dur)
    count = int(total_frames / step)
    begin = int(0.5 * (total_frames - count * step))
    end = begin + step * count
    for i in range(begin, end, step):
        librosa.display.specshow(log_chroma_spec[:, i : i + step])
        plt.axis("off")
        plt.savefig(
            f"{TEMP_DIR}/{i}.jpg",
            bbox_inches="tight",
            pad_inches=0.0,
        )
        plt.close()


def most_frequent_value(lst: list):
    counter = Counter(lst)
    max_count = max(counter.values())
    for element, count in counter.items():
        if count == max_count:
            return element

    return None


def infer(wav_path: str, log_name: str, folder_path=TEMP_DIR):
    status = "Success"
    filename = result = None
    try:
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)

        if not wav_path:
            raise ValueError("请输入音频!")

        spec = log_name.split("_")[-3]
        os.makedirs(folder_path, exist_ok=True)
        model = EvalNet(log_name, len(TRANSLATE)).model
        eval("wav2%s" % spec)(wav_path)
        jpgs = find_files(folder_path, ".jpg")
        preds = []
        for jpg in jpgs:
            input = embed_img(jpg)
            output: torch.Tensor = model(input)
            preds.append(torch.max(output.data, 1)[1])

        pred_id = most_frequent_value(preds)
        filename = os.path.basename(wav_path)
        result = TRANSLATE[CLASSES[pred_id]]

    except Exception as e:
        status = f"{e}"

    return status, filename, result


if __name__ == "__main__":
    warnings.filterwarnings("ignore")
    models = get_modelist(assign_model="alexnet_mel")
    examples = []
    example_wavs = find_files()
    for wav in example_wavs:
        examples.append([wav, models[0]])

    with gr.Blocks() as demo:
        gr.Interface(
            fn=infer,
            inputs=[
                gr.Audio(label=_L("上传录音"), type="filepath"),
                gr.Dropdown(choices=models, label=_L("选择模型"), value=models[0]),
            ],
            outputs=[
                gr.Textbox(label=_L("状态栏"), buttons=["copy"]),
                gr.Textbox(label=_L("音频文件名"), buttons=["copy"]),
                gr.Textbox(label=_L("唱法识别"), buttons=["copy"]),
            ],
            examples=examples,
            cache_examples=False,
            flagging_mode="never",
            title=_L("建议录音时长保持在 5s 左右, 过长会影响识别效率"),
        )

        gr.Markdown(
            f"# {_L('引用')}"
            + """
            ```bibtex
            @dataset{zhaorui_liu_2021_5676893,
                author    = {Zhaorui Liu and Zijin Li},
                title     = {Music Data Sharing Platform for Computational Musicology Research (CCMUSIC DATASET)},
                month     = nov,
                year      = 2021,
                publisher = {Zenodo},
                version   = {1.1},
                doi       = {10.5281/zenodo.5676893},
                url       = {https://doi.org/10.5281/zenodo.5676893}
            }
            ```"""
        )

    demo.launch(css="#gradio-share-link-button-0 { display: none; }", ssr_mode=False)
