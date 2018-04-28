#! /usr/bin/env python

import argparse
import os
import pandas as pd
from skwrapper import regress, classify, summarize


MODELS = ['LightGBM', 'RandomForest', 'XGB.1k']
CV = 3
THREADS = 4
OUT_DIR = 'p1save'
BINS = 0
CUTOFFS = None
FEATURE_SUBSAMPLE = 0


def get_parser(description=None):
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("-b", "--bins", type=int, default=BINS,
                        help="number of evenly distributed bins to make when classification mode is turned on")
    parser.add_argument("-c", "--classify",  action="store_true",
                        help="convert the regression problem into classification based on category cutoffs")
    parser.add_argument("-d", "--data",
                        help="data file to train on")
    parser.add_argument("-g", "--groupcols", nargs='+',
                        help="names of columns to be used in cross validation partitioning")
    parser.add_argument("-m", "--models", nargs='+', default=MODELS,
                        help="list of regression models: XGBoost, XGB.1K, XGB.10K, RandomForest, RF.1K, RF.10K, AdaBoost, Linear, ElasticNet, Lasso, Ridge; or list of classification models: XGBoost, XGB.1K, XGB.10K, RandomForest, RF.1K, RF.10K, AdaBoost, Logistic, Gaussian, Bayes, KNN, SVM")
    parser.add_argument("-o", "--out_dir", default=OUT_DIR,
                        help="output directory")
    parser.add_argument("-p", "--prefix",
                        help="output prefix")
    parser.add_argument("-t", "--threads", type=int, default=THREADS,
                        help="number of threads per machine learning training job; -1 for using all threads")
    parser.add_argument("-y", "--ycol", default='0',
                        help="0-based index or name of the column to be predicted")
    parser.add_argument("--cutoffs", nargs='+', type=float, default=CUTOFFS,
                        help="list of cutoffs delineating prediction target categories")
    parser.add_argument("--cv", type=int, default=CV,
                        help="cross validation folds")
    parser.add_argument("--feature_subsample", type=int, default=FEATURE_SUBSAMPLE,
                        help="number of features to randomly sample from each category, 0 means using all features")
    return parser


def main():
    parser = get_parser()
    args = parser.parse_args()

    df = pd.read_table(args.data, engine='c')
    cat_cols = df.select_dtypes(['object']).columns
    df[cat_cols] = df[cat_cols].apply(lambda x: x.astype('category').cat.codes)

    good_bins = summarize(df, ycol=args.ycol, classify=args.classify, bins=args.bins, cutoffs=args.cutoffs, min_count=args.cv)
    if args.classify and good_bins < 2:
        print('Not enough classes\n')
        return

    prefix = args.prefix or os.path.basename(args.data)
    prefix = os.path.join(args.out_dir, prefix)

    for model in args.models:
        if args.classify:
            classify(df, model, ycol=args.ycol, cv=args.cv,
                     bins=args.bins, cutoffs=args.cutoffs,
                     groupcols=args.groupcols, threads=args.threads, prefix=prefix)
        else:
            regress(df, model, ycol=args.ycol, cv=args.cv,
                    groupcols=args.groupcols, threads=args.threads, prefix=prefix)


if __name__ == '__main__':
    main()
