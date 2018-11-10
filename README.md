# ELAN-FST workflow

This repository contains the scripts used in workflows which are described in this [paper](http://www.aclweb.org/anthology/W17-0109), this [paper](http://www.aclweb.org/anthology/W17-0604) and this [poster](publications/gerstenbergerEtAl2017c.pdf). The idea is to populate lemma, part-of-speech and morphology tiers into ELAN files through open source Finite-State-Transducers developed by [Giellatekno](http://giellatekno.uit.no/) and collaborative projects with them.

The script has been tested in various projects, and the languages it has been applied to up to now are Komi-Zyrian, Kildin Saami, Pite Saami and Northern Saami.

Migration of the source code from Giellatekno SVN to GitHub was done in Giellatekno-SVN revision 162169.

## Using the scripts

The script requires FST-tools to be installed (xfst for the current version, but migration to [hfst](https://hfst.github.io/) is planned), and there is access to compiled transducers. In order to compile the transducers it is necessary to install the complete [Giellatekno infrastructure](http://giellatekno.uit.no/doc/infra/infraremake/GettingStartedWithTheNewInfra.html).

In this repository we have provided the previously compiled transducer for Komi-Zyrian, and both versions of the scripts can be run after installing lookup with:

```
git clone https://github.com/langdoc/elan-fst
python2.7 add_pos2elan_p2.7.py
```

Or:

```
python3 add_pos2elan_p3.py
```

The image below describes the ideal workflow attained using the script. Currently, Constraint Grammar based disambiguation is not included, but this is one of the improvements that are planned for near future.

![](https://imgur.com/iA99VGz.png)

### Version used for Pite Saami

The version of the Python script named `add_pos2elan_p3-sje-psdp.py` differs slightly from the other versions in two ways. First, it adds annotations on a gloss tier (child of the pos tier) with an (ideally) brief, generl English translation of the relevant lemma (translations come from an external xml file containing lemmas and translations). Second, information on the individual non-final components of compounds are also included in annotations on in the part-of-speech, morphology and gloss tiers.  This version is used in the [Pite Saami Syntax Project](http://saami.uni-freiburg.de/psdp/syntax/) (progeny of the [Pite Saami Documentation Project](http://saami.uni-freiburg.de/psdp/)); variations to the original script by Iris Perkmann and Joshua Wilbur.


## Authors

The script was written by Ciprian Gerstenberger, and collaboration in the presented workflow has taken place with Niko Partanen, Michael Rießler, Joshua Wilbur and Iris Perkmann.

## Funding

Ciprian Gerstenberger is employed by [Giellatekno](https://giellatekno.uit.no) at [The Arctic University of Norway](https://en.uit.no). Niko Partanen and Michael Rießler's work has been funded by [Kone Foundation](https://koneensaatio.fi) as part of the [IKDP-2](https://github.com/langdoc/IKDP-2) research project. Joshua Wilbur's and Iris Perkmann's contributions have been funded by [Deutsche Forschungsgemeinschaft](http://www.dfg.de) as part of the [Pite Saami Syntax Project](http://saami.uni-freiburg.de/psdp/syntax/).

## Citing

If you use the script or create new workflows based on it, please provide a link to our script in your documentation. In your  publications, please cite our papers in which we have presented and discussed our work.

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
	Editor = {Antti Arppe AND Jeff Good AND Mans Hulden AND Jordan Lachler AND Alexis Palmer AND Lane Schwartz},
	Year = {2017}}

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
	Pages = {25-36},
	Year = {2017},
	Url = {http://www.aclweb.org/anthology/W17-0604}}
```

## Licensing

Use is governed by [this GNU license](LICENSE).

