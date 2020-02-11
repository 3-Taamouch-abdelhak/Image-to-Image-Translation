import os
import torch
from torch.autograd import Variable
from torchvision.utils import save_image

from models import *
from facades import *
from utils import *

device = 'cuda' if torch.cuda.is_available() else 'cpu'


def test(batch_size):

    # Results Path #
    results_path = './data/results/generated/'
    if not os.path.exists(results_path):
        os.mkdir(results_path)

    # Prepare Data Loader #
    test_loader = get_facades_loader('test', batch_size)
    total_batch = len(test_loader)

    # Prepare Generator #
    G = Generator().to(device)
    G.load_state_dict(torch.load('./data/results/Pix2Pix_Generator.pkl'))
    G.eval()

    # Test #
    print("Generating Pix2Pix with total batch of {}.".format(total_batch))
    for i, batch in enumerate(test_loader):

        # Prepare Data #
        input = Variable(batch['A'].type(torch.FloatTensor).to(device))
        target = Variable(batch['B'].type(torch.FloatTensor).to(device))

        # Generate Fake Image #
        generated = G(input)

        # Save Images #
        result = torch.cat((target, input, generated), 0)
        result = ((result.data + 1) / 2).clamp(0, 1)
        save_image(result, os.path.join(results_path, 'Pix2Pix_Results_%03d.png' % (i+1)),
                   nrow=8, normalize=True)

    make_gifs_test("Pix2Pix", results_path)


if __name__ == '__main__':
    batch_size = 8
    test(batch_size)