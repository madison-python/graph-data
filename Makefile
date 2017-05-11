presentation.pdf: presentation.md
	pandoc \
		-f markdown -t beamer -o $@ \
		--template theme/beamer.tex \
		-V fontsize=10pt \
		$<
