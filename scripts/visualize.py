import argparse
import dataframe_helper
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import sklearn.decomposition
import sklearn.manifold



def plot_density(X, filename, xmin=None, xmax=None):
	# compute x-axis limits if not provided
	if xmin == None:
		xmin = np.nanmin(X)

	if xmax == None:
		xmax = np.nanmax(X)

	# plot the KDE of each sample
	_, ax = plt.subplots(figsize=(10, 10))

	for colname in X.columns:
		X_i = X[colname].dropna()
		sns.distplot(X_i, hist=False, ax=ax)

	plt.title("Sample Distributions")
	plt.xlabel("Expression Level")
	plt.ylabel("Density")
	plt.xlim(xmin, xmax)
	plt.savefig(filename)



def plot_tsne(X, y, filename, na_value=np.nan, n_pca=None):
	# fill missing values with a representative value
	X = X.fillna(na_value)

	# perform PCA for dimensionality reduction
	print("  Computing PCA decomposition...")

	X = X.T
	X_pca = sklearn.decomposition.PCA(n_components=n_pca, copy=False).fit_transform(X)

	# compute t-SNE from the PCA projection
	print("  Computing t-SNE...")

	X_tsne = sklearn.manifold.TSNE(n_components=2).fit_transform(X_pca)

	# plot the 2-D embedding
	plt.axis("off")

	if y.dtype.kind in "OSU":
		classes = list(set(y))

		for c in classes:
			mask = (y == c)
			plt.scatter(X_tsne[mask, 0], X_tsne[mask, 1], s=20, label=c)

		plt.legend()
	else:
		plt.scatter(X_tsne[:, 0], X_tsne[:, 1], s=20, c=y)
		plt.colorbar()

	plt.savefig(filename)



if __name__ == "__main__":
	# parse command-line arguments
	parser = argparse.ArgumentParser()
	parser.add_argument("-i", "--input", required=True, help="input expression matrix", dest="INPUT")
	parser.add_argument("--labels", help="text file of sample labels", dest="LABELS")
	parser.add_argument("--density", help="save density plot to the given filename", dest="DENSITY")
	parser.add_argument("--density-xmax", type=float, help="upper bound of x-axis", dest="DENSITY_XMAX")
	parser.add_argument("--tsne", help="save t-SNE plot to the given filename", dest="TSNE")
	parser.add_argument("--tsne-na", type=float, default=-1e3, help="numerical value to use for missing values", dest="NA_VALUE")
	parser.add_argument("--tsne-npca", type=int, help="number of principal components to take before t-SNE", dest="N_PCA")

	args = parser.parse_args()

	# load input expression matrix
	emx = dataframe_helper.load(args.INPUT)

	print("Loaded %s %s" % (args.INPUT, str(emx.shape)))

	# load label file or generate empty labels
	if args.LABELS != None:
		print("Loading label file...")

		labels = np.loadtxt(args.LABELS, dtype=str)
	else:
		labels = np.zeros(len(emx.columns), dtype=str)

	# plot sample distributions
	if args.DENSITY != None:
		print("Plotting sample distributions...")

		plot_density(emx, args.DENSITY, xmax=args.DENSITY_XMAX)

	# plot t-SNE of samples
	if args.TSNE != None:
		print("Plotting 2-D t-SNE...")

		plot_tsne(emx, labels, args.TSNE, na_value=args.NA_VALUE, n_pca=args.N_PCA)
