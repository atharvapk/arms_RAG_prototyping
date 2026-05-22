using System;
using System.Collections.Generic;
using System.Runtime.CompilerServices;
using System.Text;
using SolidWorks.Interop.sldworks;
using SolidWorks.Interop.swconst;


namespace SolidWorksAPIExample
{
    internal class Singleton
    {
        private static SldWorks? swApp;

        private Singleton()
        {

        }

        internal static SldWorks getApplication()
        {
            if (swApp == null)
            {
                swApp = Activator.CreateInstance(Type.GetTypeFromProgID("SldWorks.Application")) as SldWorks;
                swApp.Visible = true;

                return swApp;
            }

            return swApp;
        }

        internal static void Dispose()
        {
            if (swApp != null)
            {
                swApp.ExitApp();
                swApp = null;
            }
        }
    }
}
