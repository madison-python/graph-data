presentation.pdf: presentation.md
	pandoc \
		-f markdown-implicit_figures -t beamer -o $@ \
		--template theme/beamer.tex \
		$<
