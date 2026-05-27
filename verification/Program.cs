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
            program.ListAllFaceNames();

            if (args.Length > 0)
            {
                string command = args[0].ToLower();

                if (command == "colorcheck" && args.Length > 1)
                {
                    string faceName = args[1];
                    program.ExtractColorFromNamedFace(faceName);
                }
            }
            else
            {
                Console.WriteLine("\n[Notice] Run from Visual Studio: No AI arguments provided. Skipping color check.");
            }

            program.CleanUp();
        }

        public void CastObjects()
        {
            swModel = swApp.IActiveDoc2;
            swExt = swModel.Extension;
            swSelMgr = (SelectionMgr)swModel.ISelectionManager;
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
                Console.WriteLine("No tolerances found.");
                return;
            }

            for (int i = 0; i < dimCount; i++)
            {
                IDimXpertAnnotation temp = null;
                try
                {
                    temp = (IDimXpertAnnotation)dimArray[i];
                    Console.WriteLine(temp.Name);
                    Console.WriteLine($"BASIC_SIZE:{temp.Name}");
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

        public void ExtractColorFromNamedFace(string targetFaceName)
        {
            Console.WriteLine($"\n--- Searching for: {targetFaceName} ---");
            bool found = false;

            Array bodies = swPart.GetBodies2((int)swBodyType_e.swSolidBody, true) as Array;
            if (bodies == null) return;

            foreach (object bodyObj in bodies)
            {
                Body2 myBody = (Body2)bodyObj;
                Array faces = myBody.GetFaces() as Array;
                if (faces == null) continue;

                foreach (object faceObj in faces)
                {
                    Face2 myFace = (Face2)faceObj;
                    Entity myEntity = (Entity)myFace;
                    string name = swPart.GetEntityName(myEntity);

                    if (name == targetFaceName)
                    {
                        found = true;
                        double[] matProps = (double[])myFace.MaterialPropertyValues;

                        if (matProps != null)
                        {
                            int red = (int)(matProps[0] * 255);
                            int green = (int)(matProps[1] * 255);
                            int blue = (int)(matProps[2] * 255);
                            Console.WriteLine($"TARGET_FACE:{targetFaceName}");
                            Console.WriteLine($"COLOR_DATA:{red},{green},{blue}");
                        }
                        else
                        {
                            Console.WriteLine($"Found {targetFaceName}, but it has no custom color applied.");
                        }
                        break; // Exit face loop
                    }
                }
                if (found) break; // Exit body loop
            }

            if (!found)
            {
                Console.WriteLine($"Error: Could not match any face to '{targetFaceName}'.");
            }
        }

        public void ListAllFaceNames()
        {
            Console.WriteLine("\n--- Discovering all available face names ---");

            Array bodies = swPart.GetBodies2((int)swBodyType_e.swSolidBody, true) as Array;

            if (bodies == null)
            {
                Console.WriteLine("No bodies found.");
                return;
            }

            foreach (object bodyObj in bodies)
            {
                Body2 myBody = (Body2)bodyObj;
                Array faces = myBody.GetFaces() as Array;

                if (faces == null) continue;

                foreach (object faceObj in faces)
                {
                    Face2 myFace = (Face2)faceObj;

                    Entity myEntity = (Entity)myFace;
                    string name = swPart.GetEntityName(myEntity);

                    if (string.IsNullOrEmpty(name))
                    {
                        name = "No Custom Name";
                    }

                    Console.WriteLine($"Face found: '{name}'");
                }
            }
        }

        public void CleanUp()
        {
            if (dimXpertPart != null) Marshal.ReleaseComObject(dimXpertPart);
            if (dimXpertMgr != null) Marshal.ReleaseComObject(dimXpertMgr);
            if (swPart != null) Marshal.ReleaseComObject(swPart);
            if (swSelMgr != null) Marshal.ReleaseComObject(swSelMgr);
            if (swExt != null) Marshal.ReleaseComObject(swExt);
            if (swModel != null) Marshal.ReleaseComObject(swModel);
            Singleton.Dispose();
        }
    }
}