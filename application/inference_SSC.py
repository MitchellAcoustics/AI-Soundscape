import sys, os, argparse

# 这里的0是GPU id
import numpy as np

gpu_id = 1
os.environ['CUDA_VISIBLE_DEVICES'] = str(gpu_id)

sys.path.append(os.path.split(os.path.dirname(os.path.realpath(__file__)))[0])
from framework.data_generator import *
from framework.processing import *
from framework.models_pytorch import *

from sklearn import metrics


def cal_auc(predictions, targets):
    aucs = []
    for i in range(targets.shape[0]):
        test_y_auc, pred_auc = targets[i, :], predictions[i, :]
        if np.sum(test_y_auc):
            test_auc = metrics.roc_auc_score(test_y_auc, pred_auc)
            aucs.append(test_auc)
    final_auc = sum(aucs) / len(aucs)
    return final_auc


def cal_ar_rmse_mae(predictions, targets):
    rmse_loss = metrics.mean_squared_error(targets, predictions, squared=False)
    mae_loss = metrics.mean_absolute_error(targets, predictions)
    return rmse_loss, mae_loss


def count_parameters(model):
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('-model', type=str, required=True)
    args = parser.parse_args()

    model_type = args.model
    models = ['YAMNet', 'PANN', 'AST', 'DCNN_CaF_SSC']
    model_index = models.index(model_type)
    using_models = [YAMNet, PANN, ASTModel, DCNN_CaF_SSC]

    event_class = len(config.event_labels)
    model = using_models[model_index](event_class)

    params_num = count_parameters(model)
    print('Parameters num: {} M'.format(params_num / 1000 ** 2))

    model_name = model_type + config.endswith

    event_model_path = os.path.join(os.getcwd(), 'pretrained_models', model_name)
    model_event = torch.load(event_model_path, map_location='cpu')
    model.load_state_dict(model_event['state_dict'])

    cuda = 1
    if config.cuda:
        model.cuda()

    generator = DataGenerator(batch_size=64)

    data_type = 'Testing'
    generate_func = generator.generate_data(data_type=data_type, only_SSC=True)
    dict = forward_SSC(model=model, generate_func=generate_func, cuda=cuda)

    auc = cal_auc(dict['outputs_event'], dict['targets_event'])
    print("SSC:\n\tAUC: {}".format(auc))





if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv))
    except (ValueError, IOError) as e:
        sys.exit(e)














