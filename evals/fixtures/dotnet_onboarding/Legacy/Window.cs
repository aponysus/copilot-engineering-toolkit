using System.Windows.Forms;

namespace Synthetic.Desktop
{
    public static class Window
    {
        public static Form Create() => new Form { Text = "Synthetic desktop" };
    }
}
