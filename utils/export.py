from django.http import HttpResponse
from rest_framework import generics

class BaseExportExcelView(generics.GenericAPIView):
    resource_class = None
    filename = "export_data.xlsx"

    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        
        if not self.resource_class:
            raise ValueError("Kamu harus mendefinisikan 'resource_class'")
            
        resource = self.resource_class()
        dataset = resource.export(queryset)
        
        response = HttpResponse(
            dataset.xlsx, 
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{self.filename}"'
        return response