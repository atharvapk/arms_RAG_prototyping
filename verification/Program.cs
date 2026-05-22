using SolidWorks.Interop.sldworks;
using SolidWorks.Interop.swconst;
using SolidWorks.Interop.swdimxpert;
using SolidWorksAPIExample;
using System.Runtime.InteropServices;

namespace SolidWorksCircle
{
    internal class Program
    {
        public SldWorks swApp;
        IModelDoc2 swModel;
        ModelDocExtension swExt;
        SelectionMgr swSelMgr;
        PartDoc swPart;
        DimXpertPart dimXpertPart;
        DimXpertManager dimXpertMgr;

        public Program()
        {
            swApp = Singleton.getApplication();
        }
        static void Main(string[] args)
        {
            var program = new Program();
            program.CastObjects();
            program.FindTolerances();

            string command = args[0].ToLower();
            if (command == "colorcheck")
            {
                string faceName = args[1];
                program.ExtractColorFromNamedFace(faceName);
            }

            program.CleanUp();
        }
        public void CastObjects()
        {
            swModel = swApp.IActiveDoc2;
            swExt = swModel.Extension;
            swSelMgr = swModel.SelectionManager as SelectionMgr;
            swPart = swModel as PartDoc;
            dimXpertMgr = swApp.IActiveDoc2.Extension.get_DimXpertManager(swApp.IActiveDoc2.IGetActiveConfiguration().Name, true);
            dimXpertPart = (DimXpertPart)dimXpertMgr.DimXpertPart;

        }
        public void FindTolerances()
        {
            int dimCount = dimXpertPart.GetAnnotationCount();
            object[] dimArray = new object[dimCount];
            dimArray = dimXpertPart.GetAnnotations() as object[];

            if (dimArray == null)
            {
                Console.WriteLine("Damn");
                return;
            }

            for (int i = 0; i < dimCount; i++)
            {
                IDimXpertAnnotation temp = null;
                try
                {
                    temp = (IDimXpertAnnotation)dimArray[i];
                    Console.WriteLine(temp.Name);
                }
                finally
                {

                    if (temp != null)
                    {
                        Marshal.ReleaseComObject(temp);
                    }
                }
            }
        }
        public void ExtractColorFromNamedFace(string faceName)
        {
            Console.WriteLine($"--- Checking Color for Face: {faceName} ---");

            // 1. Clear any existing selections so we don't grab the wrong thing
            swModel.ClearSelection2(true);

            // 2. Tell SolidWorks to select the face by its name
            bool status = swExt.SelectByID2(faceName, "FACE", 0, 0, 0, false, 0, null, 0);

            if (status)
            {
                // 3. Grab the actual Face object from our active selection
                // The '1' means get the first thing selected.
                Face2 selectedFace = (Face2)swSelMgr.GetSelectedObject6(1, -1);

                // 4. Extract the color data
                double[] matProps = (double[])selectedFace.MaterialPropertyValues;

                if (matProps != null)
                {
                    int red = (int)(matProps[0] * 255);
                    int green = (int)(matProps[1] * 255);
                    int blue = (int)(matProps[2] * 255);

                    Console.WriteLine($"Found {faceName}! Color - R:{red} G:{green} B:{blue}");
                }
                else
                {
                    Console.WriteLine($"Found {faceName}, but it has no custom face color applied.");
                }
            }
            else
            {
                Console.WriteLine($"Error: Could not find a face named '{faceName}'. Check your spelling or MBD tree.");
            }
        }
        public void CleanUp()
        {
            Marshal.ReleaseComObject(dimXpertPart);
            Marshal.ReleaseComObject(dimXpertMgr);
            Marshal.ReleaseComObject(swPart);
            Marshal.ReleaseComObject(swSelMgr);
            Marshal.ReleaseComObject(swExt);
            Marshal.ReleaseComObject(swModel);
            Singleton.Dispose();
        }
    }
}