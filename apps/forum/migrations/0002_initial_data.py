from south.db import db
from django.db import models
from projecthub.apps.forum.models import *

class Migration:

    def forwards(self):
        # Insert initial categories
        db.execute("""INSERT INTO forum_category (id, name, position) VALUES (1, 'Discussion', 1);""")
        db.execute("""INSERT INTO forum_category (id, name, position) VALUES (2, 'Programming Questions', 2);""")
        db.execute("""INSERT INTO forum_category (id, name, position) VALUES (3, 'Suggestions & Bugs', 3);""")

        # Insert initial forums
        db.execute("INSERT INTO forum_forum (id, category_id, name, slug, description, posting_help, position) VALUES (1, 1, 'Exhibition', 'exhibition', 'Show us what you\\\'re doing with NodeBox.', '', 1);")
        db.execute("INSERT INTO forum_forum (id, category_id, name, slug, description, posting_help, position) VALUES (2, 1, 'General Discussion', 'general-discussion', 'Talk about NodeBox. This is not the place for bugs!', '', 2);")
        db.execute("INSERT INTO forum_forum (id, category_id, name, slug, description, posting_help, position) VALUES (3, 2, 'Interface', 'interface', 'Having problems with the interface? Let\\\'s talk about it.', '', 1);")
        db.execute("INSERT INTO forum_forum (id, category_id, name, slug, description, posting_help, position) VALUES (4, 2, 'Programming', 'programming', 'Talk about syntax, programming problems, etc.', '', 2);")
        db.execute("INSERT INTO forum_forum (id, category_id, name, slug, description, posting_help, position) VALUES (5, 2, 'Libraries', 'libraries', 'Discuss issues with libraries here.', '', 3);")
        db.execute("INSERT INTO forum_forum (id, category_id, name, slug, description, posting_help, position) VALUES (6, 3, 'Software suggestions', 'software-suggestions', 'You want to see something new in the software? Ask here.', '', 1);")
        db.execute("INSERT INTO forum_forum (id, category_id, name, slug, description, posting_help, position) VALUES (7, 3, 'Website suggestions', 'website-suggestions', 'Are you missing something on the website? Request it here.', '', 2);")
        db.execute("INSERT INTO forum_forum (id, category_id, name, slug, description, posting_help, position) VALUES (8, 3, 'Software bugs', 'software-bugs', 'Think something\\\'s wrong with the software? Report it here. Don\\\'t forget to search first!', '<h4>How to report bugs</h4><p>When reporting bugs, make sure you include the following information:</p><ol><li>A title that describes the bug in short, such as \\\'clicking edit while a node is selected crashes the application\\\'.</li><li>The version number of the software. Look in the About screen.</li><li>The steps you took to trigger this bug. Try to minimize this list so as not to include useless steps.</li><li>Whether you can reproduce the bug every time, or if it only happens under certain circumstances.</li></ol>', 3);")
        db.execute("INSERT INTO forum_forum (id, category_id, name, slug, description, posting_help, position) VALUES (9, 3, 'Website bugs', 'website-bugs', 'Something broken on the website? Typo in the documentation? This is the place to be.', 'Don\\\'t forget to include the URL of the page you encountered the error on.', 4);")

    def backwards(self):
        db.execute("""DELETE FROM forum_category WHERE ID=1""")
        db.execute("""DELETE FROM forum_category WHERE ID=2""")
        db.execute("""DELETE FROM forum_category WHERE ID=3""")
        db.execute("""DELETE FROM forum_forum WHERE ID=1""")
        db.execute("""DELETE FROM forum_forum WHERE ID=2""")
        db.execute("""DELETE FROM forum_forum WHERE ID=3""")
        db.execute("""DELETE FROM forum_forum WHERE ID=4""")
        db.execute("""DELETE FROM forum_forum WHERE ID=5""")
        db.execute("""DELETE FROM forum_forum WHERE ID=6""")
        db.execute("""DELETE FROM forum_forum WHERE ID=7""")
        db.execute("""DELETE FROM forum_forum WHERE ID=8""")
        db.execute("""DELETE FROM forum_forum WHERE ID=9""")
        
