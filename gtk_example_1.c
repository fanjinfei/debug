//#include <glib.h>
#include <glib/gprintf.h>
#include <gtk/gtk.h>
//gcc `pkg-config --cflags gtk+-3.0` -o example-1 example-1.c `pkg-config --libs gtk+-3.0`

/*
A convenience macro for type implementations, which declares a class initialization function, an instance initialization function (see GTypeInfo for information about these), a static variable named t_n_parent_class pointing to the parent class, and adds private instance data to the type. Furthermore, it defines a *_get_type() function. See G_DEFINE_TYPE_EXTENDED() for an example.
*/

#define PIDGIN_TYPE_MEDIA            (pidgin_media_get_type())
#define PIDGIN_MEDIA(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), PIDGIN_TYPE_MEDIA, PidginMedia))
#define PIDGIN_MEDIA_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), PIDGIN_TYPE_MEDIA, PidginMediaClass))
#define PIDGIN_IS_MEDIA(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), PIDGIN_TYPE_MEDIA))
#define PIDGIN_IS_MEDIA_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), PIDGIN_TYPE_MEDIA))
#define PIDGIN_MEDIA_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), PIDGIN_TYPE_MEDIA, PidginMediaClass))

typedef struct _PidginMedia PidginMedia;
typedef struct _PidginMediaClass PidginMediaClass;
typedef struct _PidginMediaPrivate PidginMediaPrivate;

typedef enum
{
	/* Waiting for response */
	PIDGIN_MEDIA_WAITING = 1,
	/* Got request */
	PIDGIN_MEDIA_REQUESTED,
	/* Accepted call */
	PIDGIN_MEDIA_ACCEPTED,
	/* Rejected call */
	PIDGIN_MEDIA_REJECTED,
} PidginMediaState;

struct _PidginMediaClass
{
	GtkApplicationWindowClass parent_class;
};

struct _PidginMedia
{
	GtkApplicationWindow parent;
	PidginMediaPrivate *priv;
};

enum {
	PROP_0,
	PROP_MEDIA,
	PROP_SCREENNAME
};

struct _PidginMediaPrivate
{
	gchar *media; //PurpleMedia
//	GValue screenname;
	gchar *screenname;
	gulong level_handler_id;

	GtkBuilder *ui;
	GtkWidget *menubar;
	GtkWidget *statusbar;

	GtkWidget *hold;
	GtkWidget *mute;
	GtkWidget *pause;

	GtkWidget *send_progress;
	GHashTable *recv_progressbars;

	PidginMediaState state;

	GtkWidget *display;
	GtkWidget *send_widget;
	GtkWidget *recv_widget;
	GtkWidget *button_widget;
	GtkWidget *local_video;
	GHashTable *remote_videos;

	guint timeout_id;
	//PurpleMediaSessionType request_type;
};

static GType pidgin_media_get_type(void);

G_DEFINE_TYPE_WITH_PRIVATE(PidginMedia, pidgin_media,
		GTK_TYPE_APPLICATION_WINDOW);
static void pidgin_media_dispose (GObject *object);
static void pidgin_media_get_property (GObject *object, guint prop_id, GValue *value, GParamSpec *pspec);
static void pidgin_media_set_property (GObject *object, guint prop_id, const GValue *value, GParamSpec *pspec);
		
static void
pidgin_media_class_init (PidginMediaClass *klass) {
	GObjectClass *gobject_class = G_OBJECT_CLASS(klass);

	gobject_class->dispose = pidgin_media_dispose;
//	gobject_class->finalize = pidgin_media_finalize;
	gobject_class->set_property = pidgin_media_set_property;
	gobject_class->get_property = pidgin_media_get_property;

	g_object_class_install_property(gobject_class, PROP_MEDIA,
//			g_param_spec_object("media",
			g_param_spec_string("media",
			"PurpleMedia",
			"The PurpleMedia associated with this media.",
			NULL,
			G_PARAM_CONSTRUCT_ONLY | G_PARAM_READWRITE | G_PARAM_STATIC_STRINGS));
	g_object_class_install_property(gobject_class, PROP_SCREENNAME,
			g_param_spec_string("screenname",
			"Screenname",
			"The screenname of the user this session is with.",
			NULL,
			G_PARAM_CONSTRUCT_ONLY | G_PARAM_READWRITE | G_PARAM_STATIC_STRINGS));
}

static void
pidgin_media_init (PidginMedia *media) {
    media->priv = pidgin_media_get_instance_private(media);
    //gtk_container_add(GTK_CONTAINER(media), vbox); add more widgets
}
static void
pidgin_media_dispose(GObject *media)
{
	PidginMedia *gtkmedia = PIDGIN_MEDIA(media);
	//printf("gtkmedia pidgin_media_dispose\n");

	G_OBJECT_CLASS(pidgin_media_parent_class)->dispose(media);
}

static void
pidgin_media_set_property (GObject *object, guint prop_id, const GValue *value, GParamSpec *pspec)
{
	PidginMedia *media;
	g_return_if_fail(PIDGIN_IS_MEDIA(object));

	media = PIDGIN_MEDIA(object);
	switch (prop_id) {
		case PROP_MEDIA:
		{
/*			if (media->priv->media)
				g_object_unref(media->priv->media);
			media->priv->media = g_value_dup_object(value);*/
//			g_free(media->priv->media);
			//g_value_copy(value, &media->priv->media);

/*
			g_signal_connect(G_OBJECT(media->priv->media), "error",
				G_CALLBACK(pidgin_media_error_cb), media);
			g_signal_connect(G_OBJECT(media->priv->media), "state-changed",
				G_CALLBACK(pidgin_media_state_changed_cb), media);
			g_signal_connect(G_OBJECT(media->priv->media), "stream-info",
				G_CALLBACK(pidgin_media_stream_info_cb), media);*/
			break;
		}
		case PROP_SCREENNAME:
			g_free(media->priv->screenname);
			media->priv->screenname = g_value_dup_string(value);
            g_printf("set screen name %s\n", g_value_dup_string(value));
			//g_value_copy(value, &media->priv->screenname);
			break;
		default:
			G_OBJECT_WARN_INVALID_PROPERTY_ID (object, prop_id, pspec);
			break;
	}
}
static void
pidgin_media_get_property (GObject *object, guint prop_id, GValue *value, GParamSpec *pspec)
{
	PidginMedia *media;
	g_return_if_fail(PIDGIN_IS_MEDIA(object));

	media = PIDGIN_MEDIA(object);

	switch (prop_id) {
		case PROP_MEDIA:
//			g_value_set_object(value, media->priv->media);
			g_value_set_string(value, media->priv->media);
			break;
		case PROP_SCREENNAME:
            g_printf("get screen name %s\n",media->priv->screenname);
			g_value_set_string(value, media->priv->screenname);
			break;
		default:
			G_OBJECT_WARN_INVALID_PROPERTY_ID (object, prop_id, pspec);
			break;
	}
}

static void
close_media (GtkWidget *widget,
             gpointer   data)
{
	PidginMedia *media;
	GdkWindow *window = NULL;
	g_return_if_fail(PIDGIN_IS_MEDIA(data));

	media = PIDGIN_MEDIA(data);
    g_print ("close media \n");
    gtk_widget_destroy ( GTK_WIDGET(media) );
    //window->destroy();
    
}
		
static void
print_hello (GtkWidget *widget,
             gpointer   data)
{
  int *i = data;
  g_print ("Hello World %d\n", *i);
}

int i = 10;

static void
activate (GtkApplication *app,
          gpointer        user_data)
{
  GtkWidget *window;
  GtkWidget *button;
  GtkWidget *button_box;

  window = gtk_application_window_new (app);
  gtk_window_set_title (GTK_WINDOW (window), "Window");
  gtk_window_set_default_size (GTK_WINDOW (window), 200, 200);

  button_box = gtk_button_box_new (GTK_ORIENTATION_HORIZONTAL);
  gtk_container_add (GTK_CONTAINER (window), button_box);

  button = gtk_button_new_with_label ("Hello World");
  g_signal_connect (button, "clicked", G_CALLBACK (print_hello), &i);
  g_signal_connect_swapped (button, "clicked", G_CALLBACK (gtk_widget_destroy), window);
  gtk_container_add (GTK_CONTAINER (button_box), button);

  gtk_widget_show_all (window);
}

int
main_1 (int    argc,
      char **argv)
{
  GtkApplication *app;
  int status;

  app = gtk_application_new ("org.gtk.example", G_APPLICATION_FLAGS_NONE);
  g_signal_connect (app, "activate", G_CALLBACK (activate), NULL);
  status = g_application_run (G_APPLICATION (app), argc, argv);
  g_object_unref (app);

  return status;
}
#if 0
void
viewer_file_write (ViewerFile   *self,
                   const guint8 *buffer,
                   gsize         size)
{
  g_return_if_fail (VIEWER_IS_FILE (self));
  g_return_if_fail (buffer != NULL || size == 0);

  /* First write data. */

  /* Then, notify user of data written. */
  g_signal_emit (self, file_signals[CHANGED], 0 /* details */);
}
void test() {
    
    file_signals[CHANGED] = 
      g_signal_newv ("changed",
                     G_TYPE_FROM_CLASS (object_class),
                     G_SIGNAL_RUN_LAST | G_SIGNAL_NO_RECURSE | G_SIGNAL_NO_HOOKS,
                     NULL /* closure */,
                     NULL /* accumulator */,
                     NULL /* accumulator data */,
                     NULL /* C marshaller */,
                     G_TYPE_NONE /* return_type */,
                     0     /* n_params */,
                     NULL  /* param_types */);
                     
    file = g_object_new (VIEWER_FILE_TYPE, NULL);
    g_signal_connect (file, "changed", (GCallback) print_hello, NULL);
    viewer_file_write (file, buffer, strlen (buffer));
}
#endif
int main(int argc, char *argv[])
{
    GtkWidget *window, *win_1;
    GtkWidget *myImage;
    GtkWidget *myButton, *btn;
    GtkWidget *box, *box_1;

    gtk_init(&argc, &argv);
    window = gtk_window_new(GTK_WINDOW_TOPLEVEL);
    gtk_window_set_default_size(GTK_WINDOW(window), 300, 250);
    win_1 = gtk_window_new(GTK_WINDOW_TOPLEVEL);
    gtk_window_set_default_size(GTK_WINDOW(win_1), 300, 250);


    //PidginMedia *gtkmedia = PIDGIN_MEDIA(media); //third window
    const gchar *media = "hi";
    const gchar *screenname= "we";
    /*GValue media = G_VALUE_INIT, screenname = G_VALUE_INIT;
    g_value_init (&media, G_TYPE_STRING);
    g_value_set_static_string (&media, "Hello, world!");
    g_value_init (&screenname, G_TYPE_STRING);
    g_value_set_static_string (&screenname, "Hello, world!");*/
  
    PidginMedia *gtkmedia = g_object_new(pidgin_media_get_type(),
					     "media", media,
					     "screenname", screenname, NULL);

    g_printf("print screen name %s\n", gtkmedia->priv->screenname);
    gchar *gstr;
    g_object_get (gtkmedia, "screenname", &gstr, NULL);
    g_printf("print2 screen name %s\n", gstr);

    /*
    warning: 
        ‘gtk_vbox_new’ is deprecated 
        Use 'gtk_box_new' instead
    */
    //box = gtk_vbox_new(FALSE, 0);
    box = gtk_box_new(GTK_ORIENTATION_VERTICAL, 5);
    box_1 = gtk_box_new(GTK_ORIENTATION_VERTICAL, 10);

    //myImage = gtk_image_new_from_file ("Linux.png");

    myButton = gtk_button_new_with_label("Hello GTK+ from Linux-Buddy");
    btn = gtk_button_new_with_label("Hello GTK+ from Linux-Buddy 2");
    g_signal_connect(myButton, "clicked", 
        G_CALLBACK(print_hello), &i);
    g_signal_connect(btn, "clicked", 
        G_CALLBACK(close_media), gtkmedia);

    g_signal_connect (window, "destroy", 
        G_CALLBACK(gtk_main_quit), NULL);

    
    //gtk_box_pack_start(GTK_BOX(box), myImage, TRUE, TRUE, 5);
    gtk_box_pack_end(GTK_BOX(box), myButton, TRUE, TRUE, 5);
    gtk_box_pack_end(GTK_BOX(box_1), btn, TRUE, TRUE, 5);

    gtk_container_add(GTK_CONTAINER (window), box);
    gtk_container_add(GTK_CONTAINER (win_1), box_1);
    
					     
    gtk_widget_show(GTK_WIDGET(gtkmedia));
    gtk_widget_show_all (window);
    gtk_widget_show_all (win_1);
    gtk_main();
    return(0);
}

