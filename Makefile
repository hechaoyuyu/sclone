#(c) ivali 2012/7 <hechao@ivali.com>

PREFIX = /opt
USR = /usr

.PHONY : install
.PHONY : uninstall

all:
	@echo "Makefile: Available actions: install, uninstall,"
	@echo "Makefile: Available variables: PREFIX, DESTDIR"
	
# install
install:
	-install -d $(DESTDIR)$(PREFIX)/startos-clone/
	-install -d $(DESTDIR)$(USR)/share/applications/
	-install -d $(DESTDIR)$(USR)/bin/
	-cp -r opt/* $(DESTDIR)$(PREFIX)/startos-clone
	-install sclone.desktop $(DESTDIR)$(USR)/share/applications/
	-install sclone $(DESTDIR)$(USR)/bin/sclone
	
	@echo "Makefile: startos-clone installed."


# uninstall
uninstall:
	rm -rf $(DESTDIR)$(PREFIX)/startos-clone
	rm -rf $(DESTDIR)$(USR)share/applications/sclone.desktop
	rm -rf $(DESTDIR)$(USR)/bin/sclone
	
	@echo "Makefile: startos-clone uninstall."

	
# clean	
clean:
	find opt/ -name "*.pyc" -exec rm {} \;
	

