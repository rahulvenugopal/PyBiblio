## How to manage research papers for the lab
As a young/old PI, you want to keep track of all the research publications from your lab and manage the PDFs in an efficient way (`renaming, sorting in chronological order, sort by journal etc etc`). PyBiblio is your companion.
I assume you use *Zotero* just like a `good` scientist and not something rhyming with mentally.

1. Install [Zotero](https://www.zotero.org/) and the [browser connector](https://www.zotero.org/download/)

2. You can either click and drop the PDf of research papers you have or add them using conenctor from the webpages. Have a quick proof read of the titles and other details. You can edit them if there are mistakes

![](https://github.com/rahulvenugopal/PyBiblio/blob/main/ReadmeImages/Details.png)
3. Go to `Settings` and make sure the below fields are checked

![](https://github.com/rahulvenugopal/PyBiblio/blob/main/ReadmeImages/RenameFormat.png)
4. Sometimes, you might create an entry manually and add the details (Your mentor's offline only journals from 1980s). You can scan the research paper and add the PDF copies to the citation entry

![](https://github.com/rahulvenugopal/PyBiblio/blob/main/ReadmeImages/ZoteroAddPDF.png)
5. You can custom set the naming of the PDF (say year-title-author-journal for example). Look up

![](https://github.com/rahulvenugopal/PyBiblio/blob/main/ReadmeImages/Rename.png)

6. Sometimes you need to get a bibliography (can be inserted using Zotero plugin for Libre or Word) in a specific format other than the typical Nature or APA formats. No worrries, consult your GenAI engine and generate a citation style. I created this [citation style](https://github.com/rahulvenugopal/PyBiblio/blob/main/elsevier-vancouver-reverse.csl)  which list papers in reverse chronological order

7. Now, we want to compile all the PDFs in reverse chronological order (latest first) to a single giant PDF with a neat index page and hyperlink to relevant page etc etc. Here comes the `vibe coding`

![](https://github.com/rahulvenugopal/PyBiblio/blob/main/ReadmeImages/the-simpsons-bart.gif)

8. Select the `CSV` export option and you end up with a kickass data rich CSV sheets which contains the absolute path to the PDF files as well

![](https://github.com/rahulvenugopal/PyBiblio/blob/main/ReadmeImages/ExportCSV.png)

![](https://github.com/rahulvenugopal/PyBiblio/blob/main/ReadmeImages/ExportDetails.png)

9. Now, you can run the `StitchPapers.py` vibe code given script from the same directory of `ExportedCSV` file. You will get a mega PDF with all the papers stacked in reverse chronological order. I managed to generate an index page with page number and a title page before the PDF.
Vibe coding failed to hyperlink the index page to relevant page. I will return once my GPT mana is restored

Adios amigos
