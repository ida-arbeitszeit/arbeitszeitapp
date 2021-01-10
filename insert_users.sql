INSERT INTO public.nutzer (email,"password","name",guthaben) VALUES
	 ('max@test.de','pbkdf2:sha256:150000$b39j7OaP$9aa314d2907a78ba4ca0f0c523d62eba3717a001d97340cf0ca0a0e7a437e17a','Max',0),
	 ('gregor@test.de','pbkdf2:sha256:150000$b39j7OaP$9aa314d2907a78ba4ca0f0c523d62eba3717a001d97340cf0ca0a0e7a437e17a','Gregor',0),
	 ('ruth@test.de','pbkdf2:sha256:150000$b39j7OaP$9aa314d2907a78ba4ca0f0c523d62eba3717a001d97340cf0ca0a0e7a437e17a','Ruth',0),
	 ('raphael@test.de','pbkdf2:sha256:150000$b39j7OaP$9aa314d2907a78ba4ca0f0c523d62eba3717a001d97340cf0ca0a0e7a437e17a','Raphael',0),
	 ('joerg@test.de','pbkdf2:sha256:150000$b39j7OaP$9aa314d2907a78ba4ca0f0c523d62eba3717a001d97340cf0ca0a0e7a437e17a','Jörg',0),
	 ('gaertner84@gmx.de','sha256$p8TviIXK$1420c9e4e9e553014c6eae05ffd45ab55d3dbf19ac49bbfded9da3430488735a','Sebastian',0);

INSERT INTO public.betriebe (email,"password","name",guthaben,fik) VALUES
	 ('sebastian.loschert@gmx.de','sha256$7zAxoQwe$e0a49e1e04951a939062a90d00c103f3d942ebac68c0fe01518f38cf5fbef5b3','Sebastian Loschert',0,1),
	 ('unser_betrieb@test.de','pbkdf2:sha256:150000$b39j7OaP$9aa314d2907a78ba4ca0f0c523d62eba3717a001d97340cf0ca0a0e7a437e17a','Unser Betrieb',0,1),
	 ('lieferdienst@test.de','sha256$Cwugd8XU$9091887570795d7510b7888896799dd73a59cccafdf6a9ec14fdc5277f883822','Fahrrad-Lieferdienst',0,1),
	 ('gaertner84@gmx.de','sha256$5FeH0yP1$cf6b5f1da666b3bbb0fdad59592e5d39f27a67f93cff38c30137f58d2f96f8f0','Sebas Betrieb',0,1);
