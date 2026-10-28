using System;
using Synthetic.Desktop;

internal static class Program
{
    [STAThread]
    private static int Main()
    {
        using (var window = Window.Create())
            return window.Text == "Synthetic desktop" ? 0 : 1;
    }
}
