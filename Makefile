presentation.pdf: presentation.md
	pandoc -t beamer --template theme/beamer.tex -o $@ $<
