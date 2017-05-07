presentation.pdf: presentation.md
	pandoc -t beamer -o $@ $<
