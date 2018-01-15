# ELAN-FST workflow

This repository contains the scripts used in workflows which are described in this [paper](http://www.aclweb.org/anthology/W17-0109), this [paper](http://www.aclweb.org/anthology/W17-0604) and this [poster](publications/gerstenbergerEtAl2017c.pdf). The idea is to populate lemma, pos and morph tiers into ELAN file through open source Finite-State-Transcducers developed in [Giellatekno](http://giellatekno.uit.no/).

The script has been tested in various projects, and the languages it has been applied to up to now are Komi-Zyrian, Kildin Saami, Pite Saami and Northern Saami.

Migration from Giellatekno SVN to GitHub was done in SVN Revision 162169.

## Using the scripts

The script requires FST-tools to be installed (xfst for the current version, migration to [hfst](https://hfst.github.io/) is planned), and there is access to compiled transducers. In order to compile the transducers it is necessary to install the complete [Giellatekno infrastructure](http://giellatekno.uit.no/doc/infra/infraremake/GettingStartedWithTheNewInfra.html).

In this repository we have provided an already compiled transducer for Komi-Zyrian, and the both versions of the scripts can be run after installing lookup with:

```
git clone https://github.com/langdoc/elan-fst
python2.7 add_pos2elan_p2.7.py
```

Or:

```
python3 add_pos2elan_p3.py
```

Image below describes the ideal workflow reached with the script. Currently Constraint Grammar based disambiguation is not included, but this is one the improvements that are planned in near future.

![](https://imgur.com/iA99VGz.png)

## Authors

The script is written by Ciprian Gerstenberger, and collaboration in the presented workflow has taken place with Niko Partanen, Michael Rießler and Joshua Wilbur.

## Funding

Work of Niko Partanen and Michael Rießler has been funded by [Kone Foundation](https://koneensaatio.fi) within [IKDP-2](https://github.com/langdoc/IKDP-2) research project. Joshua Wilbur's contributions have been funded by [Deutsche Forschungsgemeinschaft](http://www.dfg.de) as part of the [Pite Saami Syntax Project](http://saami.uni-freiburg.de/psdp/syntax/).

## Citing

If you use the script or create new workflows based on it, please cite the works where we have presented and discussed it.

```
@incollection{gerstenbergerEtAl2017b,
	Author = {Ciprian Gerstenberger and Niko Partanen and Michael Rie{\ss}ler},
	Booktitle = {Proceedings of the 2nd Workshop on the Use of Computational Methods in the Study of Endangered Languages},
	Location = {Honolulu},
	Month = {mar},
	Pages = {57-66},
	Publisher = {Association for Computational Linguistics},
	Series = {ACL Anthology},
	Title = {Instant annotations in ELAN corpora of spoken and written {K}omi, an endangered language of the {B}arents {S}ea region},
	Url = {http://www.aclweb.org/anthology/W17-0109},
	Year = {2017},
	Bdsk-Url-1 = {http://aclweb.org/anthology/}}

@incollection{gerstenbergerEtAl2017a,
	Author = {Ciprian Gerstenberger AND Niko Partanen AND Michael Rie{\ss}ler AND Joshua Wilbur},
	Title = {Instant annotations},
	Subtitle = {Applying {NLP} methods to the annotation of spoken language documentation corpora},
	Editor = {Tommi A. Pirinen AND Michael Rie{\ss}ler AND Trond Trosterud AND Francis M. Tyers},
	Location = {St. Petersburg},
	Month = {jan},
	Publisher = {Association for Computational Linguistics},
	Series = {ACL Anthology},
	Title = {Proceedings of the 3rd {I}nternational {W}orkshop on {C}omputational {L}inguistics for {U}ralic languages},
	Keywords = {language documentation,language technology,computational linguistics},
	Pages = {25-36},
	Year = {2017},
	Url = {http://www.aclweb.org/anthology/W17-0604}}

@misc{gerstenbergerEtAl2017c,
	Author = {Gerstenberger, Ciprian and Partanen, Niko and Rie{\ss}ler, Michael},
	Howpublished = {Poster at ComputEL-2, March 6--7, 2017, Honolulu, Hawai'i},
	Month = {mar},
	Title = {Instant annotations in {ELAN} corpora of spoken and written {K}omi-{Z}yrian, an endangered language of the {B}arents {S}ea region ({R}ussia)},
	Year = {2017},
	Bdsk-Url-1 = {http://dx.doi.org/10.13140/RG.2.2.14503.34727}}

```


