#include <gtk/gtk.h>
//gcc `pkg-config --cflags gtk+-3.0` -o example-1 example-1.c `pkg-config --libs gtk+-3.0`
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

    g_signal_connect (window, "destroy", 
        G_CALLBACK(gtk_main_quit), NULL);

    
    //gtk_box_pack_start(GTK_BOX(box), myImage, TRUE, TRUE, 5);
    gtk_box_pack_end(GTK_BOX(box), myButton, TRUE, TRUE, 5);
    gtk_box_pack_end(GTK_BOX(box_1), btn, TRUE, TRUE, 5);

    gtk_container_add(GTK_CONTAINER (window), box);
    gtk_container_add(GTK_CONTAINER (win_1), box_1);
    gtk_widget_show_all (window);
    gtk_widget_show_all (win_1);

    gtk_main();
    return(0);
}

