Yandex Search Operators – Full List Cheat Sheet

A detailed quick-reference for refining searches on Yandex Search (English version).

Reference Links

Search context (words, forms, morphology): https://yandex.com/support/search/en/query-language/search-context

Query language (pages, hosts, domains, URL operators):
https://yandex.com/support/search/en/query-language/qlanguage

Search operators (full list):
https://yandex.com/support/search/en/query-language/search-operators

Third-party advanced operators list:
https://seosly.com/blog/yandex-search-operators/

Operator Summary Table
Operator	Description	Example
!word	Exact word form only; prevents morphological variants.	!mountain
+word	Forces inclusion of the word (even stop words).	travel +to Europe
-word	Excludes results containing this word.	apple -fruit
"phrase"	Exact phrase in exact word order.	"climate change effects"
* (inside quotes)	Placeholder for any word inside exact-phrase search.	"fell down * up"
`word1	word2`	OR operator — match either word.
()	Grouping / logical subexpressions.	`(apple
url:	Search pages whose URLs begin with or contain a pattern.	url:en.wikipedia.org/wiki/*
host:	Restrict search to a specific host (exact subdomain).	host:www.example.com term
site:	Search within a website including its subdomains.	site:example.com climate
domain:	Search within a whole domain including all subdomains.	domain:edu machine learning
inurl:	Search only in the URL path.	inurl:blog security
rhost:	Reverse-host lookup; finds subdomains in wildcard fashion (OSINT).	rhost:org.example.*
mime:	Restrict results by MIME/file type.	report mime:application/pdf
date:	Restrict by date or date prefix (YYYYMMDD*).	pandemic date:202003*
lang:	Restrict by document language.	security lang:en
[]	Word-order operator: words must appear in this order; flexible spacing/forms allowed.	tickets [from London to Paris]
Full Example Queries

"cyber security" site:gov date:2023* lang:en

!apple +nutrition -virus mime:application/pdf

(machine learning | deep learning) inurl:research paper mime:pdf

company rhost:example.org lang:ru

Notes & Caveats

Some operators behave differently in Russian or morphology-rich languages.

The ! operator does not always completely block variants, depending on context.

Combine multiple operators with spaces for highly targeted searches.

rhost: is not officially documented by Yandex; derived from community/OSINT sources.

Use date: with prefixes (2023*, 202301*, etc.) for ranges.

Recommended usage:
Save this file as tools.md inside your documentation.
The table above is the best compact reference for everyday searching.