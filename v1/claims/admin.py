"""Models are registered with django admin at here."""

from django.contrib import admin

from common.admin import BaseAdmin

from v1.claims import models as claim_models


class CriterionInline(admin.TabularInline):
    """In-line view function for Sub-element model."""

    model = claim_models.Criterion
    extra = 0
    fields = ('name', 'description', 'is_mandatory', 'verification_type',)


class BatchCriterionInline(admin.TabularInline):
    """In-line view function for Sub-element model."""

    model = claim_models.BatchCriterion
    extra = 0
    fields = ('criterion', 'status')


class NodeCriterionInline(admin.TabularInline):
    """In-line view function for Sub-element model."""

    model = claim_models.NodeCriterion
    extra = 0
    fields = ('criterion', 'status')


class AttachedCriterionAdmin(BaseAdmin):
    list_display = ('criterion', 'status', 'idencode')


class BatchCriterionAdmin(BaseAdmin):
    list_select_related = (
        'batch_claim__claim', 'batch_claim__batch'
    )


class NodeCriterionAdmin(BaseAdmin):
    list_select_related = (
        'node_claim__claim', 'node_claim__node'
    )


class ClaimsAdmin(BaseAdmin):
    readonly_fields = BaseAdmin.readonly_fields
    list_display = ('name', 'type', 'idencode')
    list_filter = ('type', 'tenant')
    inlines = [
        CriterionInline,
    ]

class CriterionAdmin(BaseAdmin):
    readonly_fields = BaseAdmin.readonly_fields


class AttachedClaimAdmin(BaseAdmin):
    list_display = ('claim', 'idencode')
    list_select_related = (
        'claim',
    )


class BatchClaimAdmin(BaseAdmin):
    list_display = ('batch', 'claim', 'idencode')
    inlines = [
        BatchCriterionInline,
    ]
    list_select_related = (
        'claim', 'batch', 'batch__product'
    )


class NodeClaimAdmin(BaseAdmin):
    list_display = ('node', 'claim', 'idencode')
    inlines = [
        NodeCriterionInline,
    ]
    list_select_related = (
        'claim', 'node',
    )

class AttchedClaimCommentAdmin(BaseAdmin):
    list_display = ('attached_claim', 'creator', 'idencode')

class ClaimTransactionTypeAdmin(BaseAdmin):
    pass


admin.site.register(claim_models.Claim, ClaimsAdmin)
admin.site.register(claim_models.Criterion, CriterionAdmin)
admin.site.register(claim_models.AttachedClaim, AttachedClaimAdmin)
admin.site.register(claim_models.BatchClaim, BatchClaimAdmin)
admin.site.register(claim_models.NodeClaim, NodeClaimAdmin)
admin.site.register(claim_models.AttachedCriterion, AttachedCriterionAdmin)
admin.site.register(claim_models.BatchCriterion, BatchCriterionAdmin)
admin.site.register(claim_models.NodeCriterion, NodeCriterionAdmin)
admin.site.register(claim_models.AttachedClaimComment, AttchedClaimCommentAdmin)
admin.site.register(claim_models.ClaimTransactionType, ClaimTransactionTypeAdmin)
