import os

import torch
from torch.utils.data import DataLoader as TorchDataLoader
from torch.utils.tensorboard import SummaryWriter

import fgbg

if __name__ == "__main__":
    print(f"{fgbg.get_date_time_tag()} - started")
    output_directory = (
        "/Users/kelchtermans/data/contrastive_learning/toy_example_wwo_triplet"
    )
    os.makedirs(output_directory, exist_ok=True)
    tb_writer = SummaryWriter(log_dir=output_directory)

    print(f"{fgbg.get_date_time_tag()} - Generate dataset and data loaders")
    dataset = fgbg.SquareCircleDataset()
    train_set, val_set = torch.utils.data.random_split(
        dataset, [int(0.9 * len(dataset)), len(dataset) - int(0.9 * len(dataset))]
    )
    train_dataloader = TorchDataLoader(dataset=train_set, batch_size=100, shuffle=True)
    val_dataloader = TorchDataLoader(dataset=val_set, batch_size=100, shuffle=True)

    print(f"{fgbg.get_date_time_tag()} - Train auto-encoder with triplet loss")
    autoencoder_trplt = fgbg.AutoEncoder(
        feature_size=256, projected_size=5, decode_from_projection=True
    )
    checkpoint_file = os.path.join(
        output_directory, "checkpoint_autoencoder_trplt.ckpt"
    )
    if os.path.isfile(checkpoint_file):
        autoencoder_trplt.load_state_dict(torch.load(checkpoint_file))
    else:
        fgbg.train_autoencoder(
            autoencoder_trplt,
            train_dataloader,
            val_dataloader,
            checkpoint_file,
            tb_writer,
            triplet_loss=True,
        )

    print(f"{fgbg.get_date_time_tag()} - Train auto-encoder without triplet loss")
    autoencoder = fgbg.AutoEncoder(
        feature_size=256, projected_size=5, decode_from_projection=True
    )
    checkpoint_file = os.path.join(output_directory, "checkpoint_autoencoder.ckpt")
    if os.path.isfile(checkpoint_file):
        autoencoder.load_state_dict(torch.load(checkpoint_file))
    else:
        fgbg.train_autoencoder(
            autoencoder, train_dataloader, val_dataloader, checkpoint_file, tb_writer
        )

    print(f"{fgbg.get_date_time_tag()} - Evaluate three models")
    output_file = os.path.join(output_directory, "original")
    fgbg.evaluate_models(dataset, autoencoder_trplt, autoencoder, output_file)
    ood_dataset = fgbg.SquareDoubleCircleDataset()
    output_file = os.path.join(output_directory, "ood")
    fgbg.evaluate_models(ood_dataset, autoencoder_trplt, autoencoder, output_file)

    print(f"{fgbg.get_date_time_tag()} - finished")
