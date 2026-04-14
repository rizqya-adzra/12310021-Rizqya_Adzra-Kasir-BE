from rest_framework import serializers
from django.db import transaction as db_transaction
from apps.transaction.models import Member, Transaction, TransactionDetail

class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = ['id', 'telephone', 'name', 'point', 'created_at', 'updated_at']
        read_only_fields = ['id', 'point', 'created_at', 'updated_at']


class TransactionDetailSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')

    class Meta:
        model = TransactionDetail
        fields = ['id', 'product', 'product_name', 'price', 'quantity', 'subtotal']
        read_only_fields = ['id', 'price', 'subtotal']


class TransactionSerializer(serializers.ModelSerializer):
    details = TransactionDetailSerializer(many=True)
    
    username = serializers.ReadOnlyField(source='user.username')
    image = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = [
            'id', 'invoice', 'user', 'username', 'image', 'is_member', 'member', 'telephone', 
            'customer_name', 'payment_amount', 'change_amount', 'subtotal', 
            'is_point', 'point', 'total', 'total_quantity', 'created_at', 'details'
        ]
        read_only_fields = [
            'id', 'invoice', 'user', 'username', 'image', 'change_amount', 
            'subtotal', 'total', 'total_quantity', 'created_at' 
        ]
        
    def get_image(self, obj):
        if obj.user and hasattr(obj.user, 'image') and obj.user.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.user.image.url)
            return obj.user.image.url
        return None 

    def validate(self, attrs):
        details = attrs.get('details', [])
        if not details:
            raise serializers.ValidationError("Transaksi harus memiliki minimal 1 produk.")
        
        payment_amount = attrs.get('payment_amount', 0)
        if payment_amount <= 0:
            raise serializers.ValidationError({"payment_amount": "Jumlah uang bayar tidak valid."})
            
        return attrs

    def create(self, validated_data):
        details_data = validated_data.pop('details')
        user = self.context['request'].user
        
        is_member = validated_data.get('is_member', False)
        member = validated_data.get('member', None)
        telephone = validated_data.get('telephone')
        customer_name = validated_data.get('customer_name')
        
        is_point = validated_data.get('is_point', False)
        used_points = validated_data.get('point', 0) 
        
        if is_member and not member:
            if user.role != 'cashier':
                raise serializers.ValidationError({
                    "member": "Hanya kasir yang diperbolehkan mendaftarkan member baru."
                })
                
            if not telephone or not customer_name:
                raise serializers.ValidationError({
                    "member": "Nomor telepon dan nama pelanggan wajib diisi untuk mendaftar member baru."
                })
            
            new_member, created = Member.objects.get_or_create(
                telephone=telephone,
                defaults={'name': customer_name, 'point': 0}
            )
            validated_data['member'] = new_member
            member = new_member 

        with db_transaction.atomic():
            transaction = Transaction.objects.create(user=user, **validated_data)
            calculated_subtotal = 0
            total_items_purchased = 0
            
            for detail in details_data:
                product = detail['product']
                quantity = detail['quantity']
                
                if product.stock < quantity:
                    raise serializers.ValidationError({
                        "detail": f"Stok untuk produk {product.name} tidak mencukupi. Sisa stok: {product.stock}"
                    })
                
                product.stock -= quantity
                product.save()
                
                current_price = product.price
                item_subtotal = current_price * quantity
                calculated_subtotal += item_subtotal
                total_items_purchased += quantity  
                
                TransactionDetail.objects.create(
                    transaction=transaction,
                    product=product,
                    price=current_price,
                    quantity=quantity,
                    subtotal=item_subtotal
                )
                
            discount_from_points = 0
            
            if is_point:
                if not member:
                    raise serializers.ValidationError({
                        "point": "Pelanggan bukan member, tidak bisa menggunakan poin."
                    })
                
                if calculated_subtotal <= 20000:
                    raise serializers.ValidationError({
                        "point": "Poin hanya dapat digunakan jika total belanja di atas Rp 20.000."
                    })
                
                if used_points > member.point:
                    raise serializers.ValidationError({
                        "point": f"Poin tidak mencukupi. Sisa poin pelanggan: {member.point}"
                    })
                
                discount_from_points = used_points
                member.point -= used_points

            calculated_total = calculated_subtotal - discount_from_points
            
            if calculated_total < 0:
                calculated_total = 0
            
            payment_amount = validated_data.get('payment_amount', 0)
            if payment_amount < calculated_total:
                raise serializers.ValidationError({
                    "payment_amount": f"Uang bayar kurang! Total yang harus dibayar: {calculated_total}"
                })
                
            transaction.subtotal = calculated_subtotal
            transaction.total = calculated_total
            transaction.total_quantity = total_items_purchased 
            transaction.change_amount = payment_amount - calculated_total
            transaction.save()
            
            if is_member and member:
                gained_points = int(calculated_total * 0.02)
                
                member.point += gained_points
                member.save()
                
        return transaction