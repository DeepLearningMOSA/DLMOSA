import json
import copy
import os
from DataStruct.flatOperatorMap import FlatOperatorMap
from DataStruct.operation import Operator
from DataStruct.globalConfig import GlobalConfig
from DataStruct.edge import edge

def Decode(type, ch):
    res = 1
    same_channel_operators = [-1, 2, 4, 5, 8, 9, 10, 11, 12, 13, 14]
    if type in same_channel_operators:
        res = ch

    return res


def search_zero(in_degree, size):
    for i in range(size):
        if in_degree[i] == 0:
            return i
    return -1


def decodeChannel(f):
    global mainPath
    global branches
    #注：输入类型为flatOperaotrMap

    #先把f.chanels扩大
    f.channels = [0]*f.size
    f.channels[0] = 1
    in_degree = [0]*f.size
    for j in range(f.size):
        for i in range(f.size):
            if f.Map[i][j].m != 0:
                in_degree[j] += 1

    #最多拓扑f.size轮
    for times in range(f.size):
        # 找到入度为0的点
        target = search_zero(in_degree, f.size)
        if target < 0:
            print("Error! Circle exits!")
            return

        # mainPath.append(target + 1);
        # length = len(mainPath)
        # if length > 1:
        #     FromIndex = mainPath[length - 2] - 1
        #     ToIndex = target
        #     Operation = f.Map[FromIndex][ToIndex].m
        #     branches.append(edge(FromIndex,ToIndex,Operation))

            # for toIndex in range(f.size):
                # if toIndex == ToIndex:
                #     continue
                # if f.Map[FromIndex][toIndex].m != 0:
                #     Operation = f.Map[FromIndex][toIndex].m
                #     branches.append(edge(FromIndex, toIndex, Operation))


        in_degree[target] = -1
        for j in range(f.size):
            if f.Map[target][j].m != 0:

                # #用于引导和测试模型的专用语句 mark
                # if f.Map[target][j].m != 4:
                #     f.Map[target][j].m = 1;

                in_degree[j] -= 1
                f.channels[j] += Decode(f.Map[target][j].m, f.channels[target])
                Operation = f.Map[target][j].m
                branches.append(edge(target, j, Operation))
    # #打印各点的channels
    # print("各点的channels为：")
    # for i in range(len(f.channels)):
    #     print(i)
    #     print(f.channels[i])
    return

def parse_Type(Type):
    if Type in GlobalConfig.basicOps:
        res = GlobalConfig.basicOps.index(Type) - 1
    else:
        res = -1
    return res

if __name__ == '__main__':
    global mainPath
    global branches

    file_path = '../../result(new)/baselines/gandalf/all_models/'
    total_variety = 0
    model_num = 0
    for root, dirs, files in os.walk(file_path):
        for file in files:
            if not os.path.exists(file_path + file):
                continue
            InputPath = open(file_path + file, encoding="utf-8")
            json_dic = json.load(InputPath)
            model = json_dic['json']['network']
            f = FlatOperatorMap(size=len(model)+1)
            from_id = 0
            for each_operator in model:
                f.Map[from_id][from_id+1]=Operator(0, parse_Type(each_operator['name']))
                from_id += 1

            mainPath = []
            branches = []
            decodeChannel(f)
            for branch in branches:
                branch.channel = f.channels[branch.fromIndex]
            GlobalConfig.final_module = copy.deepcopy(branches)
            GlobalConfig.channels = copy.deepcopy(f.channels)

            from Method.get_all_connected_subgraph import get_complexity

            complexity = get_complexity()
            total_variety += complexity
            model_num += 1
            print("The variety of mode" + str(model_num) + "is:" + str(complexity))
    average_variety = total_variety / model_num
    print("average_variety:" + str(average_variety))